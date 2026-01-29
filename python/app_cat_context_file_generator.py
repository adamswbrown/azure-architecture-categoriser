import pandas as pd
import numpy as np
import json
import glob
import os
import urllib
from sqlalchemy import create_engine
import pyodbc
import re
import argparse
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


script_name =  'AppCatContextFilerCreator'

def convert_nan_to_none(obj):
    if isinstance(obj, float) and np.isnan(obj):
        return None
    elif isinstance(obj, dict):
        return {k: convert_nan_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_none(v) for v in obj]
    else:
        return obj

def script_progress(percentage,id,engine):

    status = 'InProgress' if percentage < 100.00 else 'Completed'
    timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with engine.begin() as connection:
        connection.execute(f"UPDATE dbo.ScriptExecutions SET last_edit_timestamp = '{timestamp}', percentage = {percentage}, status = '{status}' WHERE id = {id};")
        log.info(f"Table dbo.ScriptExecutions updated with status '{status}' and percentage {percentage}%")

def error_handling(error_message,id,engine):
    timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with engine.begin() as connection:
        connection.execute(f"UPDATE dbo.ScriptExecutions SET last_edit_timestamp = '{timestamp}',percentage = 100, status = 'Failed', details = '{error_message}' WHERE id = {id};")
    exit()


def load_data(log):

    quoted = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+os.environ['COMPUTERNAME']+';DATABASE=Assessments;Trusted_Connection=yes;')
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))


    if int(args.script_run_id) > 0: #script was executed from web app
        run_id = args.script_run_id

    else: #script was executed from backend
        log.info('Script executed from backend. Creating script run id.')
        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        script_id = pd.read_sql(f"SELECT TOP 1 id FROM [static].sys_scripts WHERE script_function_name = '{script_name}'",engine)['id'][0]
        with engine.begin() as connection:
            connection.execute(f""" INSERT INTO dbo.ScriptExecutions(last_edit_by, last_edit_timestamp, executed_by, executed_at, is_deleted, script_id, execution_type, percentage, status, details)
                                    VALUES('NT AUTHORITY\SYSTEM','{timestamp}','Lab3Support@drmigrate.com','{timestamp}',0,{script_id},3,0,'InProgress',NULL)""")

        run_id = pd.read_sql(f"SELECT TOP 1 id FROM dbo.ScriptExecutions WHERE script_id = {script_id} AND percentage = 0 ORDER BY id DESC",engine)['id'][0]
        log.info(f'Assigned script run id is: {run_id}.')

    log.info('Reading in app-level and server-level data.')
    try:
        output_folder = f"C:/FileUploads/AppCatFiles/{args.app_guid}"
        app_guid = args.app_guid.upper()
    except Exception as e:
        log.error(f"Error retrieving app_guid: {e}. Please ensure the app_guid is provided as a parameter.")
        error_message = f"""Dr Migrate encountered an issue creating the App Mod context file. Please contact Dr Migrate Support providing the following error code: ''PY_APP_GUID_ERROR''."""
        error_handling(error_message,run_id,engine)

    try:
    
        app_overview_df = pd.read_sql(f"""  SELECT      app.application, 
                                                        COALESCE(appq.app_type, 'Unknown') AS app_type, 
                                                        CASE WHEN appq.business_critical IS NULL THEN 'Unknown' ELSE CAST(appq.business_critical AS VARCHAR(50)) END AS business_crtiticality, 
                                                        COALESCE(app.migration_strategy, 'Unknown') AS treatment 
                                            FROM        dbo.Application app
                                            LEFT JOIN   dbo.App_Questionnaire appq
                                            ON          app.app_guid = appq.app_guid
                                            WHERE       app.app_guid = '{app_guid}'
                                        """,engine)


        vm_details_df = pd.read_sql(f"""SELECT      machine,
                                                                                                environment,
                                                                                                OperatingSystem,
                                                                                                ip_address,
                                                                                                StorageGB,
                                                                                                MemoryGB,
                                                                                                Cores,
                                                                                                CPUUsage,
                                                                                                MemoryUsage,
                                                                                                DiskReadOpsPersec,
                                                                                                DiskWriteOpsPerSec,
                                                                                                NetworkInMBPS,
                                                                                                NetworkOutMBPS,
                                                                                                StandardSSDDisks,
                                                                                                StandardHDDDisks,
                                                                                                PremiumDisks,
                                                                                                AzureVMReadiness,
                                                                                                AzureReadinessIssues,
                                                                                                migration_strategy,
                                                                                                STRING_AGG(treatment_option, ', ') AS treatment_option
                                        FROM(
                                        SELECT      DISTINCT gnm.machine,
                                                                                                gnm.environment,
                                                                                                COALESCE(vm.operating_system, aam.OperatingSystem, md.OperatingSystemDetailOSName) AS [OperatingSystem],
                                                                                                CASE WHEN vm.ip_address IS NULL OR vm.ip_address = '' THEN aam.IPAddress ELSE vm.ip_address END AS ip_address,
                                                                                                aam.StorageGB,
                                                                                                aam.MemoryMB / 1024 AS MemoryGB,
                                                                                                aam.Cores,
                                                                                                aam.CPUUsage,
                                                                                                aam.MemoryUsage,
                                                                                                aam.DiskReadOpsPersec,
                                                                                                aam.DiskWriteOpsPerSec,
                                                                                                aam.NetworkInMBPS,
                                                                                                aam.NetworkOutMBPS,
                                                                                                aam.StandardSSDDisks,
                                                                                                aam.StandardHDDDisks,
                                                                                                aam.PremiumDisks,
                                                                                                aam.AzureVMReadiness,
                                                                                                aam.AzureReadinessIssues,
                                                                                                st.migration_strategy,
                                                                                                CASE WHEN sto.treatment_option = 'Other' THEN sto.treatment_option_other ELSE sto.treatment_option END AS treatment_option
                                                                                                -- RIGHTSIZING!!!!
                                                                                    FROM        dbo.GUID_Name_Mapping gnm
                                                                                    LEFT JOIN   dbo.Virtual_Machines vm
                                                                                    ON          gnm.vm_guid = vm.vm_guid
                                                                                    LEFT JOIN   dbo.Migration_Report_All_Assessed_Machines_latest aam
                                                                                    ON          gnm.machine = aam.Machine
                                                                                    LEFT JOIN   dbo.MachineDiscovery_latest md
                                                                                    ON          gnm.machine = md.DisplayName
                                                                                    LEFT JOIN   dbo.Server_Treatment st
                                                                                    ON          vm.vm_guid = st.vm_guid
                                                                                    LEFT JOIN   dbo.Server_Treatment_Options sto
                                                                                    ON          st.id = sto.server_treatment_id
                                                                                    WHERE       gnm.app_guid = '{app_guid}'
                                                                                    AND         sto.is_active = 1
                                                                                    GROUP BY    gnm.machine,
                                                                                                gnm.environment,
                                                                                                vm.operating_system,
                                                                                                aam.OperatingSystem,
                                                                                                md.OperatingSystemDetailOSName,
                                                                                                vm.ip_address,
                                                                                                aam.IPAddress,
                                                                                                aam.StorageGB,
                                                                                                aam.MemoryMB,
                                                                                                aam.Cores,
                                                                                                aam.CPUUsage,
                                                                                                aam.MemoryUsage,
                                                                                                aam.StandardSSDDisks,
                                                                                                aam.StandardHDDDisks,
                                                                                                aam.PremiumDisks,
                                                                                                aam.AzureVMReadiness,
                                                                                                aam.AzureReadinessIssues,
                                                                                                st.migration_strategy,
                                                                                                sto.treatment_option_other,
                                                                                                aam.DiskReadOpsPersec,
                                                                                                aam.DiskWriteOpsPerSec,
                                                                                                aam.NetworkInMBPS,
                                                                                                aam.NetworkOutMBPS,
                                                                                                sto.treatment_option,
                                                                                                sto.treatment_option_other)a
                                        GROUP BY machine,
                                                                                                environment,
                                                                                                OperatingSystem,
                                                                                                ip_address,
                                                                                                StorageGB,
                                                                                                MemoryGB,
                                                                                                Cores,
                                                                                                CPUUsage,
                                                                                                MemoryUsage,
                                                                                                DiskReadOpsPersec,
                                                                                                DiskWriteOpsPerSec,
                                                                                                NetworkInMBPS,
                                                                                                NetworkOutMBPS,
                                                                                                StandardSSDDisks,
                                                                                                StandardHDDDisks,
                                                                                                PremiumDisks,
                                                                                                AzureVMReadiness,
                                                                                                AzureReadinessIssues,
                                                                                                migration_strategy
                                        """,engine)

        vm_software_df = pd.read_sql(f"""   SELECT      DISTINCT sc.DisplayName AS machine,
                                                        COALESCE(sc.version, sc.FriendlyName) AS detected_COTS,
                                                        trr.treatment_option AS approved_solution
                                                        -- sc.SoftwareGrouping,
                                                        -- sc.ServerCategory,
                                                        -- sc.ServerSubCategory
                                            FROM        dbo.GUID_Name_Mapping gnm
                                            LEFT JOIN   dbo.MachineDiscovery_latest md
                                            ON          gnm.machine = md.DisplayName
                                            LEFT JOIN   dbo.ServerCategory sc
                                            ON          gnm.machine = sc.DisplayName
                                            OR          md.MachineId = sc.VM_ID
                                            INNER JOIN  static.Modernisation_Options mo
                                            ON          sc.FriendlyName = mo.FriendlyName
                                            LEFT JOIN   semi_static.TreatmentQueriesRules trr
                                            ON          COALESCE(sc.version, sc.FriendlyName) = trr.technology
                                            WHERE       gnm.app_guid = '{app_guid}'
                                            AND        ((sc.ServerCategory = 'Web Server' OR (sc.SoftwareGrouping = 'App Stack' AND sc.ServerCategory = 'Application' OR sc.FriendlyName = 'PHP'))
                                            AND         Conclusion = 'Confirmed'
                                            OR          ( sc.SoftwareGrouping IN ('Platform Service', 'Utility', 'Security','Modern Workplace')
                                                            AND  sc.Type = 'Master'
                                                            AND  sc.Conclusion = 'Confirmed')
                                                            OR (sc.ServerCategory = 'Middleware'))

                                            """,engine)
        vm_software_df_grouped = vm_software_df.groupby('machine',as_index=False).agg({'detected_COTS':'unique'})

        vm_details_df = vm_details_df.merge(vm_software_df_grouped,how='left',on='machine')
        vm_details_df['detected_COTS'] = [c.tolist() if isinstance(c,np.ndarray) else None for c in vm_details_df['detected_COTS']]
        vm_details_df['ip_address'] = vm_details_df.ip_address.str.replace(';','').str.replace('[', '').str.replace(']','').str.strip().str.split(',')
        vm_details_df[['StorageGB','MemoryGB','Cores','CPUUsage','MemoryUsage','DiskReadOpsPersec','DiskWriteOpsPerSec','NetworkInMBPS','NetworkOutMBPS','StandardSSDDisks','StandardHDDDisks','PremiumDisks']] = vm_details_df[['StorageGB','MemoryGB','Cores','CPUUsage','MemoryUsage','DiskReadOpsPersec','DiskWriteOpsPerSec','NetworkInMBPS','NetworkOutMBPS','StandardSSDDisks','StandardHDDDisks','PremiumDisks']].replace('',0).fillna(0).astype(float)

        vm_dict = dict({'server_details':vm_details_df.to_dict(orient='records')})
        detected_cots_dict = {'detected_technology_running':vm_software_df['detected_COTS'].drop_duplicates().tolist()}
        approved_solutions_dict = {'app_approved_azure_services':[vm_software_df[['detected_COTS', 'approved_solution']].drop_duplicates().set_index('detected_COTS')['approved_solution'].to_dict()]}
        app_dict = dict({'app_overview':app_overview_df.to_dict(orient='records')}) | detected_cots_dict | approved_solutions_dict


    except pyodbc.InterfaceError as e: # incorrect db credentials
        log.error(f"Error retrieving app-level or server-level data due to: {e}.")
        error_code = re.search(r" \((\d+)\) ",str(e)).group(1)
        error_message = f"""Dr Migrate encountered an error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_{error_code}_ERROR''."""
        error_handling(error_message,run_id,engine)
    
    except pyodbc.DatabaseError as e: #closed db connection or incorrect server
        log.error(f"Error retrieving app-level or server-level data due to: {e}.")
        if re.search(r" \((\d+)\) ",str(e)) is None:    
            if 'closed connection' in str(e):
                error_code = 'CLOSED_CONNECTION'
            else:
                error_code = 'UNKNOWN'
        else:
            error_code = re.search(r" \((\d+)\) ",str(e)).group(1)
        error_message = f"""Dr Migrate encountered an error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_{error_code}_ERROR''."""
        error_handling(error_message,run_id,engine)

    except Exception as e:
        log.error(f"Error retrieving app-level or server-level data due to: {e}.")
        error_code = re.search(r" \((\d+)\) ",str(e)).group(1)
        if error_code.isdigit() == True:
            error_message = f"""Dr Migrate encountered an unexpected error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_{error_code}_ERROR''."""
        else:
            error_message = f"""Dr Migrate encountered an unexpected error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_UNKNOWN_ERROR''."""
        error_handling(error_message,run_id,engine)

    app_name = pd.read_sql(f"SELECT application FROM dbo.Application WHERE app_guid = '{app_guid}'", engine)['application'].iat[0]


    # log.info('Reading in network data.')

    # ### NETWORK DATA
    # try:
    #     # Load VM data
    #     Virtual_Machines = pd.read_sql('SELECT machine FROM dbo.Virtual_Machines', engine)
    #     Virtual_Machines['machine'] = Virtual_Machines.machine.str.upper()

    #     GUID_Name_Mapping = pd.read_sql("SELECT DISTINCT UPPER(machine) AS machine, UPPER(app_guid) AS app_guid, application FROM dbo.GUID_Name_Mapping WHERE application <> 'Unassociated Servers'", engine)
    #     app_name = GUID_Name_Mapping[GUID_Name_Mapping.app_guid.str.upper() == app_guid]['application'].iat[0]

    #     GUID_Name_Mapping = GUID_Name_Mapping.drop('app_guid',axis=1)

    # except pyodbc.InterfaceError as e: # incorrect db credentials
    #     log.error(f"Error retrieving netowrk metadata due to: {e}.")
    #     error_code = re.search(r" \((\d+)\) ",str(e)).group(1)
    #     error_message = f"""Dr Migrate encountered an error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_{error_code}_ERROR''."""
    #     error_handling(error_message,run_id,engine)
    
    # except pyodbc.DatabaseError as e: #closed db connection or incorrect server
    #     log.error(f"Error retrieving netowrk metadata due to: {e}.")
    #     if re.search(r" \((\d+)\) ",str(e)) is None:    
    #         if 'closed connection' in str(e):
    #             error_code = 'CLOSED_CONNECTION'
    #         else:
    #             error_code = 'UNKNOWN'
    #     else:
    #         error_code = re.search(r" \((\d+)\) ",str(e)).group(1)
    #     error_message = f"""Dr Migrate encountered an error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_{error_code}_ERROR''."""
    #     error_handling(error_message,run_id,engine)

    # except Exception as e:
    #     log.error(f"Error retrieving netowrk metadata due to: {e}.")
    #     error_code = re.search(r" \((\d+)\) ",str(e)).group(1)
    #     if error_code.isdigit() == True:
    #         error_message = f"""Dr Migrate encountered an unexpected error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_{error_code}_ERROR''."""
    #     else:
    #         error_message = f"""Dr Migrate encountered an unexpected error. Please contact Dr Migrate Support providing the following error code: ''PY_DB_UNKNOWN_ERROR''."""
    #     error_handling(error_message,run_id,engine)

    # # log.info(f'Loading network data')
    # parquet_file = []
    # os.chdir("C:\\Network_Connections\\")
    # for file in glob.glob("*.parquet"):
    #     parquet_file.append(file)

    # network_data = {}
    # for file in parquet_file:
    #     network_data[file] = pd.read_parquet(f'C:\\Network_Connections\\{file}', engine='pyarrow')
    #     network_data[file]['Destination port'] = network_data[file]['Destination port'].astype(str)
    # try:
    #     network_data = pd.concat(network_data)
    #     log.info(f"""Number of total unique VMs detected: {len(list(pd.unique(network_data[['Source server name','Destination server name']].values.ravel('K')))):,}""")

    # except:
    #     network_data = pd.DataFrame(columns=['Source server name','Destination server name'])
    # #check to see if there is usable network data
    # try:
    #     log.info('Transforming data.')
    #     # Create an vm to vm comms dataframe
    #     network_data['source_machine'] = network_data['Source server name'].str.upper()
    #     network_data['target_machine'] = network_data['Destination server name'].str.upper()
    #     vm_to_vm_comms = network_data[(network_data['source_machine'] != network_data['target_machine'])].reset_index(drop=True)
    #     vm_to_vm_comms = vm_to_vm_comms[vm_to_vm_comms['source_machine'].notnull()].reset_index(drop=True)
    #     vm_to_vm_comms = vm_to_vm_comms[vm_to_vm_comms['target_machine'].notnull()].reset_index(drop=True)
    #     # vm_to_vm_comms = vm_to_vm_comms[(vm_to_vm_comms.source_machine.isin(Virtual_Machines.machine.unique())) & (vm_to_vm_comms.target_machine.isin(Virtual_Machines.machine.unique()))]
        
    #     # Create a mapping dictionary
    #     GUID_Name_Mapping = dict(zip(GUID_Name_Mapping['machine'], GUID_Name_Mapping['application']))

    #     # Map vm to app
    #     vm_to_vm_comms['source_app'] = vm_to_vm_comms['source_machine'].map(GUID_Name_Mapping)
    #     vm_to_vm_comms['target_app'] = vm_to_vm_comms['target_machine'].map(GUID_Name_Mapping)

    #     # vm_to_vm_comms = vm_to_vm_comms[['source_m','target_m','source_app','target_app','Destination port']]
    #     vm_to_vm_comms['Destination port'] = pd.to_numeric(vm_to_vm_comms['Destination port'].astype(float))
    #     vm_to_vm_comms['direction'] = np.where(vm_to_vm_comms.source_app == app_name, 'outbound',
    #                                 np.where(vm_to_vm_comms.target_app == app_name, 'inbound',None))
    #     vm_to_vm_comms = vm_to_vm_comms[vm_to_vm_comms.direction.notnull()]

    #     outbound_df = vm_to_vm_comms[vm_to_vm_comms.direction == 'outbound'].drop_duplicates()
    #     inbound_df = vm_to_vm_comms[vm_to_vm_comms.direction == 'inbound'].drop_duplicates()

    #     apps_communictes_with = [guid for guid in list(set(list(outbound_df.target_app[outbound_df.target_app.notnull()].unique()) + list(inbound_df.source_app[inbound_df.source_app.notnull()].unique()))) if guid != app_name]
    #     unique_inbound_ports = inbound_df['Destination port'].unique()
    #     unique_outbound_ports = outbound_df['Destination port'].unique()

    #     vm_to_vm_comms = vm_to_vm_comms[['direction', 'source_machine',  'source_app', 'target_machine','target_app','Source IP', 'Source application', 'Source process', 'Destination IP','Destination application', 'Destination process', 'Destination port']].drop_duplicates()
    #     vm_to_vm_comms[['Source application','Destination application']] = vm_to_vm_comms[['Source application','Destination application']].fillna('Unknown application')

    #     vm_to_vm_comms = vm_to_vm_comms.groupby(['direction','source_machine','source_app','target_machine','target_app','Source IP','Destination IP','Destination port'],as_index=False).agg({'Source application':'unique', 'Source process':'unique', 'Destination application':'unique', 'Destination process':'unique'})
    #     vm_to_vm_comms[['Source application', 'Source process', 'Destination application', 'Destination process']] = vm_to_vm_comms[['Source application', 'Source process', 'Destination application', 'Destination process']] .applymap(list)

    #     vm_to_vm_comms['Source application'] = [l[0] if len(l) == 1 else l for l in vm_to_vm_comms['Source application']]
    #     vm_to_vm_comms['Source process'] = [l[0] if len(l) == 1 else l for l in vm_to_vm_comms['Source process']]
    #     vm_to_vm_comms['Destination application'] = [l[0] if len(l) == 1 else l for l in vm_to_vm_comms['Destination application']]
    #     vm_to_vm_comms['Destination process'] = [l[0] if len(l) == 1 else l for l in vm_to_vm_comms['Destination process']]

    #     nw_export_dict = dict({'app_name':app_name}) | dict({'app_integrations_with':apps_communictes_with}) | dict({'inbound_ports':list(unique_inbound_ports)}) | dict({'outbound_ports':list(unique_outbound_ports)}) | dict({'network_details':vm_to_vm_comms.to_dict(orient='records')})

    #     nw_export_dict = dict({'network_insights':nw_export_dict})

    # except:
    #     log.error(f'No useable network data found. Exiting process.')
    #     nw_export_dict = dict({'network_insights':{}})

    log.info('Retrieving results file.')
    relevant_files = ["result.json"]
    technology = args.technology
    results_file= {'App Mod results': []}
    results_path = f'C:/FileUploads/AppCatFiles/{app_guid}/{technology}'

    if not os.path.exists(results_path):
        os.makedirs(results_path)
        results_file = {}
        log.info('No App Mod results uploaded. Proceeding without results file.')

    else:
        for root, dirs, files in os.walk(results_path):
            for file in files:
                if file in relevant_files:
                    log.info(f"{file} detected")
                    
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            results_file = {'App Mod results':[json.load(f)]}


    log.info('Generating context json file.') 
    # context_file = app_dict | vm_dict | nw_export_dict | results_file
    context_file = app_dict | vm_dict | results_file
    context_file = [convert_nan_to_none(context_file)]
    app_name = app_name.replace(' ','_')

    log.info(f"Saving '{app_name}_context_file.json' in '{output_folder}'.") 
    
    with open(f'{output_folder}/{app_name}_{technology}_context_file.json', 'w') as f:
        json.dump(context_file, f, indent=4, default=int)


    script_progress(100.00,run_id,engine)

    log.info('Process completed.')

def set_logging():
    # create logger
    level = "INFO"
    if args.verbose:
        level = "DEBUG"
    logger = logging.getLogger("Dr Migrate Logging")
    logger.setLevel(level)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)
    return logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dr Migrate Application Complexity Rater.")
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Verbose Logging",
    )
    parser.add_argument(
        "-guid",
        "--app_guid",
        dest="app_guid",
        required=True,
        help='app_guid for application context file.',
    )
    parser.add_argument(
        "-id",
        "--run_id",
        dest="script_run_id",
        default=0,
        required=False,
        help='AppCat context file generator script_run_id.',
    )
    parser.add_argument(
        "-tech",
        "--technology",
        dest="technology",
        required=True,
        help='AppCat context file generator technology (i.e. Java or ,Net).',
    )
    args = parser.parse_args()
    
    log = set_logging()
    load_data(log)