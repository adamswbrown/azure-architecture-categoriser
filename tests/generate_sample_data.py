#!/usr/bin/env python3
"""
Generate Sample Context Files for Azure Architecture Recommender

This script generates realistic sample context files that demonstrate
different application migration scenarios. These files are used for:
- Testing the scoring engine
- Demonstrating the tool's capabilities to users
- Providing examples of the expected input format

Usage:
    python tests/generate_sample_data.py [--output-dir DIR] [--scenario NAME]

Examples:
    # Generate all sample files
    python tests/generate_sample_data.py

    # Generate to a custom directory
    python tests/generate_sample_data.py --output-dir ./my-samples

    # Generate a specific scenario
    python tests/generate_sample_data.py --scenario java-refactor-aks

    # List all available scenarios
    python tests/generate_sample_data.py --list
"""

import argparse
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class AppOverview:
    """Application overview section."""
    application: str
    app_type: str
    business_crtiticality: str  # Note: typo matches Dr. Migrate output
    treatment: str
    cost_priority: Optional[str] = None
    budget_constraint: Optional[str] = None
    compliance_requirements: Optional[list[str]] = None
    availability_requirement: Optional[str] = None


@dataclass
class ServerDetails:
    """Server details section."""
    machine: str
    environment: str
    OperatingSystem: str
    ip_address: list[str]
    StorageGB: float
    MemoryGB: float
    Cores: float
    CPUUsage: float
    MemoryUsage: float
    DiskReadOpsPersec: float
    DiskWriteOpsPerSec: float
    NetworkInMBPS: float
    NetworkOutMBPS: float
    StandardSSDDisks: float
    StandardHDDDisks: float
    PremiumDisks: float
    AzureVMReadiness: str
    AzureReadinessIssues: Optional[str]
    migration_strategy: str
    treatment_option: str
    detected_COTS: list[str]
    treatment_option_other: Optional[str] = None


@dataclass
class AppModFinding:
    """Individual finding from app modernization assessment."""
    type: str
    severity: str
    description: str


@dataclass
class AppModResults:
    """App modernization results section."""
    technology: str
    summary: dict
    findings: list[dict]
    compatibility: dict
    recommended_targets: list[str]
    blockers: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    """A complete scenario definition."""
    id: str
    name: str
    description: str
    expected_recommendations: list[str]
    expected_confidence: str
    app_overview: AppOverview
    detected_technology: list[str]
    approved_services: dict
    servers: list[ServerDetails]
    app_mod_results: list[AppModResults]

    def to_context(self) -> list[dict]:
        """Convert to context file format."""
        return [{
            "app_overview": [{
                k: v for k, v in asdict(self.app_overview).items() if v is not None
            }],
            "detected_technology_running": self.detected_technology,
            "app_approved_azure_services": [self.approved_services],
            "server_details": [
                {k: v for k, v in asdict(s).items() if v is not None}
                for s in self.servers
            ],
            "App Mod results": [
                {
                    "technology": r.technology,
                    "summary": r.summary,
                    "findings": r.findings,
                    "compatibility": r.compatibility,
                    "recommended_targets": r.recommended_targets,
                    "blockers": r.blockers
                }
                for r in self.app_mod_results
            ]
        }]


# =============================================================================
# SCENARIO DEFINITIONS
# =============================================================================
# Each scenario demonstrates a different migration pattern and expected outcome

SCENARIOS: list[Scenario] = [
    # -------------------------------------------------------------------------
    # 1. Java Refactor to AKS - Cloud-Native Transformation
    # -------------------------------------------------------------------------
    Scenario(
        id="01-java-refactor-aks",
        name="Java Spring Boot Refactor to AKS",
        description="""
        Modern Java Spring Boot application ready for containerization.
        - 6 microservices with externalized configuration
        - Already uses message queues (RabbitMQ)
        - PostgreSQL database
        - Fully container-ready

        Expected: AKS-based architectures, high confidence
        """,
        expected_recommendations=["AKS Baseline", "Microservices on AKS"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="OrderProcessingPlatform",
            app_type="Distributed Application",
            business_crtiticality="Medium",
            treatment="Refactor"
        ),
        detected_technology=["Java 11", "Spring Boot", "Apache Tomcat", "RabbitMQ", "PostgreSQL"],
        approved_services={
            "Apache Tomcat": "Azure Kubernetes Service",
            "RabbitMQ": "Azure Service Bus",
            "PostgreSQL": "Azure Database for PostgreSQL"
        },
        servers=[ServerDetails(
            machine="ORDERSVC01",
            environment="Production",
            OperatingSystem="Ubuntu 20.04",
            ip_address=["10.20.0.5"],
            StorageGB=120.0,
            MemoryGB=8.0,
            Cores=4.0,
            CPUUsage=55.0,
            MemoryUsage=65.0,
            DiskReadOpsPersec=90.0,
            DiskWriteOpsPerSec=70.0,
            NetworkInMBPS=28.0,
            NetworkOutMBPS=32.0,
            StandardSSDDisks=1.0,
            StandardHDDDisks=0.0,
            PremiumDisks=0.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Refactor",
            treatment_option="Containerize, Refactor",
            detected_COTS=["Java 11", "Spring Boot", "Apache Tomcat"]
        )],
        app_mod_results=[AppModResults(
            technology="Java",
            summary={
                "services_scanned": 6,
                "spring_boot_apps": 6,
                "externalized_configuration": True,
                "container_ready": True
            },
            findings=[{
                "type": "Configuration",
                "severity": "Low",
                "description": "Configuration externalized via environment variables."
            }],
            compatibility={
                "azure_app_service": "Supported",
                "azure_container_apps": "Supported",
                "azure_kubernetes_service": "FullySupported"
            },
            recommended_targets=["Azure Kubernetes Service", "Azure Container Apps"],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 2. .NET Replatform to App Service
    # -------------------------------------------------------------------------
    Scenario(
        id="02-dotnet-replatform-appservice",
        name=".NET Core Replatform to App Service",
        description="""
        .NET Core web application suitable for PaaS.
        - Simple 3-tier architecture
        - SQL Server database
        - No containerization needed

        Expected: App Service architectures, high confidence
        """,
        expected_recommendations=["App Service Baseline", "Web App with SQL"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="CustomerPortal",
            app_type="Web Application",
            business_crtiticality="High",
            treatment="Replatform"
        ),
        detected_technology=[".NET Core 6.0", "ASP.NET Core MVC", "SQL Server 2019", "IIS"],
        approved_services={
            "IIS": "Azure App Service",
            "SQL Server": "Azure SQL Database"
        },
        servers=[ServerDetails(
            machine="WEBPORTAL01",
            environment="Production",
            OperatingSystem="Windows Server 2019",
            ip_address=["10.10.0.10"],
            StorageGB=100.0,
            MemoryGB=16.0,
            Cores=4.0,
            CPUUsage=35.0,
            MemoryUsage=50.0,
            DiskReadOpsPersec=50.0,
            DiskWriteOpsPerSec=30.0,
            NetworkInMBPS=15.0,
            NetworkOutMBPS=20.0,
            StandardSSDDisks=1.0,
            StandardHDDDisks=0.0,
            PremiumDisks=0.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Replatform",
            treatment_option="PaaS Migration",
            detected_COTS=[".NET Core", "SQL Server", "IIS"]
        )],
        app_mod_results=[AppModResults(
            technology=".NET",
            summary={
                "services_scanned": 1,
                "dotnet_version": "6.0",
                "app_service_compatible": True
            },
            findings=[{
                "type": "Platform",
                "severity": "Low",
                "description": ".NET Core 6.0 fully supported on Azure App Service."
            }],
            compatibility={
                "azure_app_service": "FullySupported",
                "azure_container_apps": "Supported",
                "azure_kubernetes_service": "Supported"
            },
            recommended_targets=["Azure App Service", "Azure SQL Database"],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 3. Legacy Tolerate - Minimal Change
    # -------------------------------------------------------------------------
    Scenario(
        id="03-legacy-tolerate",
        name="Legacy VB6 Application - Tolerate",
        description="""
        Legacy VB6 application that cannot be modernized.
        - No source code available
        - Runs on Windows Server 2012
        - Required for compliance

        Expected: VM-based lift-and-shift, low confidence
        """,
        expected_recommendations=["Azure VM", "IaaS Baseline"],
        expected_confidence="medium",
        app_overview=AppOverview(
            application="LegacyReporting",
            app_type="Desktop Application",
            business_crtiticality="Low",
            treatment="Tolerate"
        ),
        detected_technology=["Visual Basic 6.0", "Microsoft Access", "COM Components"],
        approved_services={
            "Visual Basic 6.0": "Azure Virtual Machines"
        },
        servers=[ServerDetails(
            machine="LEGACY01",
            environment="Production",
            OperatingSystem="Windows Server 2012 R2",
            ip_address=["10.5.0.50"],
            StorageGB=80.0,
            MemoryGB=4.0,
            Cores=2.0,
            CPUUsage=10.0,
            MemoryUsage=25.0,
            DiskReadOpsPersec=10.0,
            DiskWriteOpsPerSec=5.0,
            NetworkInMBPS=2.0,
            NetworkOutMBPS=1.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=1.0,
            PremiumDisks=0.0,
            AzureVMReadiness="ReadyWithConditions",
            AzureReadinessIssues="Legacy OS requires extended support",
            migration_strategy="Rehost",
            treatment_option="Lift and Shift",
            detected_COTS=["Visual Basic 6.0", "Microsoft Access"]
        )],
        app_mod_results=[AppModResults(
            technology="Legacy",
            summary={
                "services_scanned": 1,
                "modernization_viable": False,
                "source_available": False
            },
            findings=[{
                "type": "Blocker",
                "severity": "High",
                "description": "No source code available for modernization."
            }, {
                "type": "Platform",
                "severity": "Medium",
                "description": "VB6 requires Windows VM with legacy support."
            }],
            compatibility={
                "azure_app_service": "NotSupported",
                "azure_container_apps": "NotSupported",
                "azure_vm": "Supported"
            },
            recommended_targets=["Azure Virtual Machines"],
            blockers=["No source code", "Legacy runtime dependencies"]
        )]
    ),

    # -------------------------------------------------------------------------
    # 4. Mixed Java/.NET - Partial Modernization
    # -------------------------------------------------------------------------
    Scenario(
        id="04-mixed-java-dotnet-partial-appmod",
        name="Mixed Java/.NET with Partial Modernization",
        description="""
        Enterprise application with both Java and .NET components.
        - Java backend services (can modernize)
        - .NET legacy frontend (must tolerate)
        - Complex integration requirements

        Expected: Hybrid approach, medium confidence
        """,
        expected_recommendations=["Hybrid Cloud", "App Service + AKS"],
        expected_confidence="medium",
        app_overview=AppOverview(
            application="EnterpriseERP",
            app_type="Distributed Application",
            business_crtiticality="High",
            treatment="Refactor"
        ),
        detected_technology=[
            "Java 17", "Spring Boot", ".NET Framework 4.8",
            "SQL Server 2019", "Oracle Database", "RabbitMQ"
        ],
        approved_services={
            "Java Services": "Azure Kubernetes Service",
            ".NET Frontend": "Azure App Service",
            "SQL Server": "Azure SQL Database",
            "Oracle": "Oracle on Azure VM"
        },
        servers=[
            ServerDetails(
                machine="JAVA-API01",
                environment="Production",
                OperatingSystem="Ubuntu 22.04",
                ip_address=["10.30.0.10"],
                StorageGB=200.0,
                MemoryGB=32.0,
                Cores=8.0,
                CPUUsage=60.0,
                MemoryUsage=70.0,
                DiskReadOpsPersec=150.0,
                DiskWriteOpsPerSec=100.0,
                NetworkInMBPS=50.0,
                NetworkOutMBPS=45.0,
                StandardSSDDisks=2.0,
                StandardHDDDisks=0.0,
                PremiumDisks=0.0,
                AzureVMReadiness="Ready",
                AzureReadinessIssues=None,
                migration_strategy="Refactor",
                treatment_option="Containerize",
                detected_COTS=["Java 17", "Spring Boot", "RabbitMQ"]
            ),
            ServerDetails(
                machine="DOTNET-WEB01",
                environment="Production",
                OperatingSystem="Windows Server 2019",
                ip_address=["10.30.0.20"],
                StorageGB=100.0,
                MemoryGB=16.0,
                Cores=4.0,
                CPUUsage=40.0,
                MemoryUsage=55.0,
                DiskReadOpsPersec=60.0,
                DiskWriteOpsPerSec=40.0,
                NetworkInMBPS=25.0,
                NetworkOutMBPS=30.0,
                StandardSSDDisks=1.0,
                StandardHDDDisks=0.0,
                PremiumDisks=0.0,
                AzureVMReadiness="Ready",
                AzureReadinessIssues=None,
                migration_strategy="Replatform",
                treatment_option="PaaS Migration",
                detected_COTS=[".NET Framework 4.8", "IIS"]
            )
        ],
        app_mod_results=[
            AppModResults(
                technology="Java",
                summary={
                    "services_scanned": 5,
                    "spring_boot_apps": 5,
                    "container_ready": True
                },
                findings=[{
                    "type": "Architecture",
                    "severity": "Low",
                    "description": "Java services are container-ready."
                }],
                compatibility={
                    "azure_kubernetes_service": "FullySupported",
                    "azure_container_apps": "Supported"
                },
                recommended_targets=["Azure Kubernetes Service"],
                blockers=[]
            ),
            AppModResults(
                technology=".NET",
                summary={
                    "services_scanned": 1,
                    "framework_version": "4.8",
                    "modernization_effort": "High"
                },
                findings=[{
                    "type": "Platform",
                    "severity": "Medium",
                    "description": ".NET Framework 4.8 requires Windows hosting."
                }],
                compatibility={
                    "azure_app_service": "Supported",
                    "azure_container_apps": "NotSupported"
                },
                recommended_targets=["Azure App Service (Windows)"],
                blockers=["Full .NET Framework dependency"]
            )
        ]
    ),

    # -------------------------------------------------------------------------
    # 5. Greenfield Cloud-Native
    # -------------------------------------------------------------------------
    Scenario(
        id="07-greenfield-cloud-native-perfect",
        name="Greenfield Cloud-Native Application",
        description="""
        New cloud-native application designed for Azure.
        - Kubernetes-native design
        - Event-driven architecture
        - Full CI/CD pipeline
        - No legacy constraints

        Expected: Cloud-native architectures, very high confidence
        """,
        expected_recommendations=["AKS Baseline", "Microservices", "Event-Driven"],
        expected_confidence="very_high",
        app_overview=AppOverview(
            application="CloudNativeCommerce",
            app_type="Microservices",
            business_crtiticality="High",
            treatment="Rebuild"
        ),
        detected_technology=[
            "Go 1.21", "Kubernetes", "Kafka", "Redis",
            "PostgreSQL", "gRPC", "Prometheus", "Grafana"
        ],
        approved_services={
            "Kubernetes": "Azure Kubernetes Service",
            "Kafka": "Azure Event Hubs",
            "Redis": "Azure Cache for Redis",
            "PostgreSQL": "Azure Database for PostgreSQL"
        },
        servers=[ServerDetails(
            machine="K8S-NODE01",
            environment="Production",
            OperatingSystem="Ubuntu 22.04",
            ip_address=["10.50.0.10"],
            StorageGB=500.0,
            MemoryGB=64.0,
            Cores=16.0,
            CPUUsage=45.0,
            MemoryUsage=60.0,
            DiskReadOpsPersec=200.0,
            DiskWriteOpsPerSec=150.0,
            NetworkInMBPS=100.0,
            NetworkOutMBPS=120.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=0.0,
            PremiumDisks=2.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Rebuild",
            treatment_option="Cloud-Native",
            detected_COTS=["Kubernetes", "Kafka", "PostgreSQL"]
        )],
        app_mod_results=[AppModResults(
            technology="Cloud-Native",
            summary={
                "services_scanned": 12,
                "kubernetes_native": True,
                "event_driven": True,
                "ci_cd_ready": True,
                "observability_enabled": True
            },
            findings=[{
                "type": "Architecture",
                "severity": "Info",
                "description": "Application designed for cloud-native deployment."
            }],
            compatibility={
                "azure_kubernetes_service": "FullySupported",
                "azure_container_apps": "Supported",
                "azure_event_hubs": "FullySupported"
            },
            recommended_targets=[
                "Azure Kubernetes Service",
                "Azure Event Hubs",
                "Azure Cache for Redis",
                "Azure Database for PostgreSQL"
            ],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 6. VM Lift-and-Shift
    # -------------------------------------------------------------------------
    Scenario(
        id="09-rehost-vm-lift-shift",
        name="VM Lift-and-Shift Migration",
        description="""
        Traditional application requiring VM-based hosting.
        - Custom C++ services
        - Specialized hardware requirements
        - Cannot be containerized

        Expected: IaaS/VM architectures, high confidence
        """,
        expected_recommendations=["Azure VM", "IaaS Baseline"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="CADProcessingEngine",
            app_type="Batch Application",
            business_crtiticality="Medium",
            treatment="Rehost"
        ),
        detected_technology=["C++", "CUDA", "OpenGL", "SQL Server 2019"],
        approved_services={
            "C++ Services": "Azure Virtual Machines (GPU)",
            "SQL Server": "SQL Server on Azure VM"
        },
        servers=[ServerDetails(
            machine="CAD-PROC01",
            environment="Production",
            OperatingSystem="Windows Server 2022",
            ip_address=["10.60.0.10"],
            StorageGB=2000.0,
            MemoryGB=128.0,
            Cores=32.0,
            CPUUsage=70.0,
            MemoryUsage=75.0,
            DiskReadOpsPersec=500.0,
            DiskWriteOpsPerSec=400.0,
            NetworkInMBPS=200.0,
            NetworkOutMBPS=150.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=0.0,
            PremiumDisks=4.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Rehost",
            treatment_option="Lift and Shift",
            detected_COTS=["C++", "CUDA", "SQL Server"]
        )],
        app_mod_results=[AppModResults(
            technology="Native",
            summary={
                "services_scanned": 1,
                "gpu_required": True,
                "specialized_hardware": True
            },
            findings=[{
                "type": "Hardware",
                "severity": "Info",
                "description": "Application requires GPU compute capabilities."
            }],
            compatibility={
                "azure_vm_gpu": "FullySupported",
                "azure_batch": "Supported"
            },
            recommended_targets=["Azure Virtual Machines (NC/ND series)"],
            blockers=["GPU dependency", "Native code"]
        )]
    ),

    # -------------------------------------------------------------------------
    # 7. Healthcare Regulated
    # -------------------------------------------------------------------------
    Scenario(
        id="13-highly-regulated-healthcare",
        name="Healthcare Application (HIPAA Compliant)",
        description="""
        Healthcare application with strict compliance requirements.
        - HIPAA compliance required
        - PHI data handling
        - Audit logging mandatory
        - Data residency requirements

        Expected: Regulated/compliant architectures, high confidence
        """,
        expected_recommendations=["Healthcare Baseline", "Compliant Web App"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="PatientRecordsSystem",
            app_type="Web Application",
            business_crtiticality="Critical",
            treatment="Replatform",
            compliance_requirements=["HIPAA", "HITECH"],
            availability_requirement="zone_redundant"
        ),
        detected_technology=[".NET 8", "SQL Server 2022", "Azure AD B2C", "Redis"],
        approved_services={
            ".NET App": "Azure App Service (Isolated)",
            "SQL Server": "Azure SQL Database (Business Critical)",
            "Cache": "Azure Cache for Redis (Premium)"
        },
        servers=[ServerDetails(
            machine="HEALTH-WEB01",
            environment="Production",
            OperatingSystem="Windows Server 2022",
            ip_address=["10.100.0.10"],
            StorageGB=500.0,
            MemoryGB=32.0,
            Cores=8.0,
            CPUUsage=40.0,
            MemoryUsage=55.0,
            DiskReadOpsPersec=100.0,
            DiskWriteOpsPerSec=80.0,
            NetworkInMBPS=30.0,
            NetworkOutMBPS=25.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=0.0,
            PremiumDisks=2.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Replatform",
            treatment_option="Compliant PaaS",
            detected_COTS=[".NET 8", "SQL Server"]
        )],
        app_mod_results=[AppModResults(
            technology=".NET",
            summary={
                "services_scanned": 1,
                "hipaa_controls_present": True,
                "encryption_at_rest": True,
                "audit_logging": True
            },
            findings=[{
                "type": "Compliance",
                "severity": "Info",
                "description": "Application has HIPAA-required security controls."
            }, {
                "type": "Data",
                "severity": "Medium",
                "description": "PHI data requires isolated environment."
            }],
            compatibility={
                "azure_app_service_isolated": "FullySupported",
                "azure_sql_business_critical": "FullySupported"
            },
            recommended_targets=[
                "Azure App Service Environment",
                "Azure SQL (Business Critical)",
                "Azure Key Vault (Premium)"
            ],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 8. Startup Cost-Optimized
    # -------------------------------------------------------------------------
    Scenario(
        id="17-cost-minimized-startup",
        name="Startup MVP (Cost Optimized)",
        description="""
        Startup application prioritizing minimal costs.
        - Variable/low traffic patterns
        - Consumption-based pricing preferred
        - Stateless architecture

        Expected: Serverless/consumption architectures, high confidence
        """,
        expected_recommendations=["Static Web Apps", "Functions", "Serverless"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="StartupMVP",
            app_type="Web Application",
            business_crtiticality="Medium",
            treatment="Replatform",
            cost_priority="cost_minimized",
            budget_constraint="minimal"
        ),
        detected_technology=["Node.js 20", "Express.js", "MongoDB", "React"],
        approved_services={
            "Node.js": "Azure App Service (Free/Basic)",
            "MongoDB": "Azure Cosmos DB (Serverless)"
        },
        servers=[ServerDetails(
            machine="STARTUP-WEB01",
            environment="Production",
            OperatingSystem="Ubuntu 22.04",
            ip_address=["10.140.0.5"],
            StorageGB=20.0,
            MemoryGB=2.0,
            Cores=1.0,
            CPUUsage=15.0,
            MemoryUsage=30.0,
            DiskReadOpsPersec=20.0,
            DiskWriteOpsPerSec=15.0,
            NetworkInMBPS=5.0,
            NetworkOutMBPS=4.0,
            StandardSSDDisks=1.0,
            StandardHDDDisks=0.0,
            PremiumDisks=0.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Replatform",
            treatment_option="Serverless/consumption pricing",
            detected_COTS=["Node.js", "MongoDB"]
        )],
        app_mod_results=[AppModResults(
            technology="Node.js",
            summary={
                "services_scanned": 1,
                "stateless": True,
                "container_ready": True,
                "low_traffic": True,
                "variable_load": True
            },
            findings=[{
                "type": "Cost",
                "severity": "Low",
                "description": "Low traffic patterns ideal for consumption-based pricing."
            }, {
                "type": "Architecture",
                "severity": "Low",
                "description": "Stateless application suitable for serverless deployment."
            }],
            compatibility={
                "azure_app_service_free": "Supported",
                "azure_functions": "Supported",
                "azure_container_apps_consumption": "Supported",
                "azure_static_web_apps": "Supported"
            },
            recommended_targets=[
                "Azure App Service (Basic tier)",
                "Azure Functions (Consumption)",
                "Azure Cosmos DB (Serverless)",
                "Azure Static Web Apps (Free)"
            ],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 9. AI/ML Innovation
    # -------------------------------------------------------------------------
    Scenario(
        id="18-innovation-first-ai-ml",
        name="AI/ML Innovation Platform",
        description="""
        AI/ML application requiring specialized compute.
        - Machine learning workloads
        - GPU requirements
        - Large dataset processing
        - MLOps pipeline

        Expected: AI/ML architectures, high confidence
        """,
        expected_recommendations=["Azure ML", "AI Workbench", "Data Science"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="MLPredictionEngine",
            app_type="AI/ML Application",
            business_crtiticality="High",
            treatment="Rebuild"
        ),
        detected_technology=[
            "Python 3.11", "PyTorch", "TensorFlow", "Kubernetes",
            "Apache Spark", "Delta Lake", "MLflow"
        ],
        approved_services={
            "ML Training": "Azure Machine Learning",
            "Data Lake": "Azure Data Lake Storage",
            "Compute": "Azure Machine Learning Compute"
        },
        servers=[ServerDetails(
            machine="ML-TRAIN01",
            environment="Production",
            OperatingSystem="Ubuntu 22.04",
            ip_address=["10.150.0.10"],
            StorageGB=5000.0,
            MemoryGB=256.0,
            Cores=64.0,
            CPUUsage=80.0,
            MemoryUsage=85.0,
            DiskReadOpsPersec=1000.0,
            DiskWriteOpsPerSec=800.0,
            NetworkInMBPS=500.0,
            NetworkOutMBPS=400.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=0.0,
            PremiumDisks=8.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Rebuild",
            treatment_option="Cloud ML Platform",
            detected_COTS=["Python", "PyTorch", "Kubernetes"]
        )],
        app_mod_results=[AppModResults(
            technology="Python/ML",
            summary={
                "services_scanned": 1,
                "ml_frameworks": ["PyTorch", "TensorFlow"],
                "gpu_required": True,
                "mlops_enabled": True
            },
            findings=[{
                "type": "Compute",
                "severity": "Info",
                "description": "ML workloads require GPU compute clusters."
            }, {
                "type": "Data",
                "severity": "Info",
                "description": "Large datasets require data lake storage."
            }],
            compatibility={
                "azure_machine_learning": "FullySupported",
                "azure_databricks": "FullySupported"
            },
            recommended_targets=[
                "Azure Machine Learning",
                "Azure Data Lake Storage Gen2",
                "Azure Databricks"
            ],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 10. Mainframe COBOL
    # -------------------------------------------------------------------------
    Scenario(
        id="19-appmod-blockers-mainframe",
        name="Mainframe COBOL Application",
        description="""
        Legacy mainframe application with modernization blockers.
        - COBOL/CICS application
        - Tight mainframe coupling
        - Critical business logic
        - No modernization path

        Expected: Limited options, requires assessment
        """,
        expected_recommendations=["Azure VM", "Partner Solutions"],
        expected_confidence="low",
        app_overview=AppOverview(
            application="CoreBankingLedger",
            app_type="Mainframe Application",
            business_crtiticality="Critical",
            treatment="Retain"
        ),
        detected_technology=["COBOL", "CICS", "DB2", "JCL", "VSAM"],
        approved_services={
            "Mainframe": "Specialized Assessment Required"
        },
        servers=[ServerDetails(
            machine="MAINFRAME-LPAR01",
            environment="Production",
            OperatingSystem="z/OS",
            ip_address=["10.200.0.1"],
            StorageGB=10000.0,
            MemoryGB=512.0,
            Cores=100.0,
            CPUUsage=65.0,
            MemoryUsage=70.0,
            DiskReadOpsPersec=5000.0,
            DiskWriteOpsPerSec=3000.0,
            NetworkInMBPS=1000.0,
            NetworkOutMBPS=800.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=0.0,
            PremiumDisks=0.0,
            AzureVMReadiness="NotReady",
            AzureReadinessIssues="Mainframe workload requires specialized assessment",
            migration_strategy="Retain",
            treatment_option="Specialized modernization",
            detected_COTS=["COBOL", "CICS", "DB2"]
        )],
        app_mod_results=[AppModResults(
            technology="Mainframe",
            summary={
                "services_scanned": 1,
                "modernization_viable": False,
                "specialized_platform": True
            },
            findings=[{
                "type": "Blocker",
                "severity": "Critical",
                "description": "Mainframe workload requires specialized modernization approach."
            }, {
                "type": "Platform",
                "severity": "High",
                "description": "COBOL/CICS has limited Azure native options."
            }],
            compatibility={
                "azure_app_service": "NotSupported",
                "azure_kubernetes_service": "NotSupported",
                "azure_vm": "Requires Partner Solution"
            },
            recommended_targets=["Partner Mainframe Modernization"],
            blockers=["Mainframe platform", "COBOL runtime", "CICS dependency"]
        )]
    ),

    # -------------------------------------------------------------------------
    # 11. Mission-Critical Multi-Region
    # -------------------------------------------------------------------------
    Scenario(
        id="14-multi-region-active-active",
        name="Mission-Critical Multi-Region",
        description="""
        Mission-critical application requiring multi-region deployment.
        - 99.99% availability requirement
        - Active-active across regions
        - Global user base
        - Real-time data replication

        Expected: Multi-region architectures, high confidence
        """,
        expected_recommendations=["Multi-Region", "Mission-Critical", "Global"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="GlobalTradingPlatform",
            app_type="Distributed Application",
            business_crtiticality="Critical",
            treatment="Refactor",
            availability_requirement="multi_region_active_active"
        ),
        detected_technology=[
            "Java 21", "Spring Boot", "Kafka", "Cassandra",
            "Redis", "Kubernetes"
        ],
        approved_services={
            "Application": "Azure Kubernetes Service",
            "Messaging": "Azure Event Hubs",
            "Database": "Azure Cosmos DB",
            "Cache": "Azure Cache for Redis"
        },
        servers=[
            ServerDetails(
                machine="TRADE-US-EAST",
                environment="Production",
                OperatingSystem="Ubuntu 22.04",
                ip_address=["10.170.0.10"],
                StorageGB=1000.0,
                MemoryGB=128.0,
                Cores=32.0,
                CPUUsage=50.0,
                MemoryUsage=60.0,
                DiskReadOpsPersec=500.0,
                DiskWriteOpsPerSec=400.0,
                NetworkInMBPS=200.0,
                NetworkOutMBPS=180.0,
                StandardSSDDisks=0.0,
                StandardHDDDisks=0.0,
                PremiumDisks=4.0,
                AzureVMReadiness="Ready",
                AzureReadinessIssues=None,
                migration_strategy="Refactor",
                treatment_option="Multi-region active-active",
                detected_COTS=["Java", "Kafka", "Cassandra"]
            ),
            ServerDetails(
                machine="TRADE-EU-WEST",
                environment="Production",
                OperatingSystem="Ubuntu 22.04",
                ip_address=["10.171.0.10"],
                StorageGB=1000.0,
                MemoryGB=128.0,
                Cores=32.0,
                CPUUsage=45.0,
                MemoryUsage=55.0,
                DiskReadOpsPersec=450.0,
                DiskWriteOpsPerSec=350.0,
                NetworkInMBPS=180.0,
                NetworkOutMBPS=160.0,
                StandardSSDDisks=0.0,
                StandardHDDDisks=0.0,
                PremiumDisks=4.0,
                AzureVMReadiness="Ready",
                AzureReadinessIssues=None,
                migration_strategy="Refactor",
                treatment_option="Multi-region active-active",
                detected_COTS=["Java", "Kafka", "Cassandra"]
            )
        ],
        app_mod_results=[AppModResults(
            technology="Java/Cloud-Native",
            summary={
                "services_scanned": 20,
                "multi_region_ready": True,
                "stateless_services": True,
                "event_driven": True
            },
            findings=[{
                "type": "Architecture",
                "severity": "Info",
                "description": "Application designed for multi-region deployment."
            }, {
                "type": "Data",
                "severity": "Info",
                "description": "Cassandra supports multi-region replication."
            }],
            compatibility={
                "azure_kubernetes_service": "FullySupported",
                "azure_cosmos_db": "FullySupported",
                "azure_front_door": "FullySupported"
            },
            recommended_targets=[
                "Azure Kubernetes Service (Multi-region)",
                "Azure Cosmos DB (Multi-master)",
                "Azure Front Door",
                "Azure Traffic Manager"
            ],
            blockers=[]
        )]
    ),

    # -------------------------------------------------------------------------
    # 12. Traditional IT ERP
    # -------------------------------------------------------------------------
    Scenario(
        id="15-traditional-it-erp",
        name="Traditional IT - SAP ERP",
        description="""
        SAP ERP system with traditional IT operations model.
        - SAP S/4HANA
        - Standard change management
        - IT service desk operations
        - Vendor-supported platform

        Expected: SAP on Azure architectures, high confidence
        """,
        expected_recommendations=["SAP on Azure", "Enterprise ERP"],
        expected_confidence="high",
        app_overview=AppOverview(
            application="CorporateERP",
            app_type="ERP System",
            business_crtiticality="Critical",
            treatment="Replatform"
        ),
        detected_technology=["SAP S/4HANA", "SAP HANA", "ABAP", "SAP Fiori"],
        approved_services={
            "SAP Application": "Azure VMs (Certified for SAP)",
            "SAP HANA": "Azure Large Instances or VMs"
        },
        servers=[ServerDetails(
            machine="SAP-APP01",
            environment="Production",
            OperatingSystem="SUSE Linux Enterprise Server 15",
            ip_address=["10.180.0.10"],
            StorageGB=5000.0,
            MemoryGB=512.0,
            Cores=64.0,
            CPUUsage=55.0,
            MemoryUsage=65.0,
            DiskReadOpsPersec=800.0,
            DiskWriteOpsPerSec=600.0,
            NetworkInMBPS=300.0,
            NetworkOutMBPS=250.0,
            StandardSSDDisks=0.0,
            StandardHDDDisks=0.0,
            PremiumDisks=8.0,
            AzureVMReadiness="Ready",
            AzureReadinessIssues=None,
            migration_strategy="Replatform",
            treatment_option="SAP on Azure",
            detected_COTS=["SAP S/4HANA", "SAP HANA"]
        )],
        app_mod_results=[AppModResults(
            technology="SAP",
            summary={
                "services_scanned": 1,
                "sap_certified": True,
                "hana_database": True
            },
            findings=[{
                "type": "Platform",
                "severity": "Info",
                "description": "SAP workload eligible for Azure certified VMs."
            }],
            compatibility={
                "azure_vm_sap_certified": "FullySupported",
                "azure_large_instances": "Supported"
            },
            recommended_targets=[
                "Azure VMs (M-series for SAP)",
                "Azure NetApp Files",
                "Azure Site Recovery"
            ],
            blockers=[]
        )]
    ),
]


def generate_scenario(scenario: Scenario, output_dir: Path) -> Path:
    """Generate a single scenario file."""
    filename = f"{scenario.id}.json"
    filepath = output_dir / filename

    context = scenario.to_context()

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(context, f, indent=2)

    return filepath


def generate_all(output_dir: Path) -> list[Path]:
    """Generate all scenario files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []

    for scenario in SCENARIOS:
        filepath = generate_scenario(scenario, output_dir)
        files.append(filepath)
        print(f"Generated: {filepath.name}")

    return files


def list_scenarios() -> None:
    """List all available scenarios."""
    print("\nAvailable Scenarios:")
    print("=" * 80)

    for scenario in SCENARIOS:
        print(f"\n{scenario.id}")
        print(f"  Name: {scenario.name}")
        print(f"  Expected Confidence: {scenario.expected_confidence}")
        print(f"  Expected Recommendations: {', '.join(scenario.expected_recommendations)}")
        print(f"  Description: {scenario.description.strip()[:100]}...")


def generate_index(output_dir: Path) -> None:
    """Generate an index file with scenario descriptions."""
    index_path = output_dir / "README.md"

    content = """# Sample Context Files

This directory contains sample context files for testing and demonstrating
the Azure Architecture Recommender.

## Scenarios

| File | Name | Treatment | Expected Confidence |
|------|------|-----------|---------------------|
"""

    for scenario in SCENARIOS:
        content += f"| `{scenario.id}.json` | {scenario.name} | {scenario.app_overview.treatment} | {scenario.expected_confidence} |\n"

    content += """
## Usage

These files can be used with:

1. **Recommendations App** - Upload any file to get architecture recommendations
2. **CLI Scorer** - `architecture-scorer score --context <file>.json`
3. **Testing** - Automated tests use these as fixtures

## Regenerating

To regenerate these files:

```bash
python tests/generate_sample_data.py
```

## Adding New Scenarios

Edit `tests/generate_sample_data.py` and add a new `Scenario` object to the
`SCENARIOS` list. Run the generator to create the file.

## Schema

Each context file follows the Dr. Migrate output format:

```json
[{
  "app_overview": [{
    "application": "AppName",
    "app_type": "Web Application",
    "business_crtiticality": "High",
    "treatment": "Refactor"
  }],
  "detected_technology_running": ["Java 11", "Spring Boot"],
  "app_approved_azure_services": [{
    "Java": "Azure Kubernetes Service"
  }],
  "server_details": [...],
  "App Mod results": [...]
}]
```
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nGenerated index: {index_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate sample context files for Azure Architecture Recommender"
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'examples' / 'context_files',
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--scenario',
        type=str,
        help='Generate only a specific scenario by ID'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available scenarios'
    )
    parser.add_argument(
        '--index-only',
        action='store_true',
        help='Only generate the index file'
    )

    args = parser.parse_args()

    if args.list:
        list_scenarios()
        return

    if args.index_only:
        generate_index(args.output_dir)
        return

    if args.scenario:
        scenario = next((s for s in SCENARIOS if s.id == args.scenario), None)
        if not scenario:
            print(f"Error: Scenario '{args.scenario}' not found")
            print("Use --list to see available scenarios")
            return
        args.output_dir.mkdir(parents=True, exist_ok=True)
        filepath = generate_scenario(scenario, args.output_dir)
        print(f"Generated: {filepath}")
    else:
        print(f"Generating sample data to: {args.output_dir}")
        generate_all(args.output_dir)
        generate_index(args.output_dir)
        print(f"\nGenerated {len(SCENARIOS)} scenario files")


if __name__ == "__main__":
    main()
