import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import re
from collections import Counter
import PyPDF2

# Page configuration
st.set_page_config(
    page_title="Legal AI Automation Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Comprehensive LegalBench Task Categories with automation potential
# Based on 162 tasks from LegalBench framework
LEGALBENCH_TASKS = {
    # CONTRACT ANALYSIS & REVIEW (High automation 85-95%)
    'Contract-Clause-Identification': {
        'description': 'Identifying and extracting specific contract clauses (CUAD tasks)',
        'automation_potential': 0.92,
        'keywords': ['anti-assignment', 'audit rights', 'cap on liability', 'change of control', 
                    'competitive restriction', 'covenant not to sue', 'effective date', 'exclusivity',
                    'expiration date', 'governing law', 'insurance', 'ip ownership', 'license grant',
                    'liquidated damages', 'minimum commitment', 'most favored nation', 'non-compete',
                    'notice period', 'post-termination', 'price restrictions', 'renewal term',
                    'revenue share', 'rofr', 'source code escrow', 'termination', 'warranty duration',
                    'volume restriction', 'unlimited liability', 'clause review', 'provision'],
        'examples': ['CUAD contract review', 'Clause extraction', 'Contract provision identification']
    },
    'Contract-NLI-Analysis': {
        'description': 'Natural language inference for contract interpretation',
        'automation_potential': 0.88,
        'keywords': ['confidentiality', 'explicit identification', 'limited use', 'no licensing',
                    'notice on disclosure', 'permissible copy', 'sharing with employees',
                    'sharing with third parties', 'survival of obligations', 'contract entailment',
                    'agreement interpretation', 'contract meaning'],
        'examples': ['Contract clause interpretation', 'Confidentiality analysis', 'Obligation identification']
    },
    'Contract-QA': {
        'description': 'Question answering about contract terms and provisions',
        'automation_potential': 0.85,
        'keywords': ['contract question', 'agreement terms', 'what does contract say', 'contract provision',
                    'consumer contract', 'terms of service', 'contract language'],
        'examples': ['Contract Q&A', 'Consumer contract analysis', 'Terms clarification']
    },
    
    # M&A AND CORPORATE (Medium-High automation 75-90%)
    'MA-Deal-Terms': {
        'description': 'M&A deal terms analysis (MAUD tasks)',
        'automation_potential': 0.82,
        'keywords': ['maud', 'accuracy of target', 'accuracy of fundamental', 'capitalization',
                    'matching rights', 'buyer consent', 'change in law', 'changes in gaap',
                    'cor permitted', 'cor standard', 'intervening event', 'liability standard',
                    'ordinary course', 'pandemic', 'public health', 'relational language',
                    'tail period', 'type of consideration', 'merger agreement', 'acquisition'],
        'examples': ['M&A agreement review', 'Deal term extraction', 'Acquisition document analysis']
    },
    'Corporate-Transactions': {
        'description': 'Corporate transaction elements and terms',
        'automation_potential': 0.80,
        'keywords': ['ability to consummate', 'accounting principles', 'negative covenant',
                    'outstanding shares', 'superior offer', 'no shop', 'shop breach',
                    'determination trigger', 'transferable license', 'corporate action'],
        'examples': ['Transaction document review', 'Corporate covenant analysis', 'Deal structure review']
    },
    'Corporate-Governance': {
        'description': 'Corporate governance and compliance matters',
        'automation_potential': 0.75,
        'keywords': ['corporate lobbying', 'supply chain disclosure', 'best practice audits',
                    'disclosed training', 'governance', 'compliance disclosure', 'corporate policy'],
        'examples': ['Corporate lobbying analysis', 'Supply chain compliance', 'Disclosure review']
    },
    
    # LITIGATION & PROCEDURE (Medium automation 70-85%)
    'Case-Law-Analysis': {
        'description': 'Case law research and citation analysis',
        'automation_potential': 0.90,
        'keywords': ['citation prediction', 'citation open', 'overruling', 'precedent',
                    'case law', 'judicial decision', 'court opinion', 'legal authority'],
        'examples': ['Citation research', 'Precedent analysis', 'Case law review']
    },
    'Legal-Issue-Spotting': {
        'description': 'Identifying legal issues across practice areas (Learned Hands)',
        'automation_potential': 0.85,
        'keywords': ['learned hands', 'business law', 'consumer law', 'courts', 'crime',
                    'divorce', 'domestic violence', 'education law', 'employment law',
                    'estates', 'family law', 'health law', 'housing law', 'immigration',
                    'torts', 'legal issue', 'identify problem', 'legal matter'],
        'examples': ['Issue identification', 'Practice area classification', 'Legal problem spotting']
    },
    'Litigation-Documents': {
        'description': 'Securities complaints and litigation document analysis',
        'automation_potential': 0.87,
        'keywords': ['securities complaint', 'ssla', 'company defendants', 'individual defendants',
                    'plaintiff', 'complaint extraction', 'litigation document', 'pleading'],
        'examples': ['Complaint analysis', 'Securities litigation review', 'Pleading extraction']
    },
    'Procedural-Analysis': {
        'description': 'Court procedures and jurisdiction',
        'automation_potential': 0.75,
        'keywords': ['personal jurisdiction', 'diversity jurisdiction', 'oral argument',
                    'question purpose', 'function of decision', 'court procedure'],
        'examples': ['Jurisdiction analysis', 'Procedural review', 'Court filing analysis']
    },
    
    # REGULATORY & COMPLIANCE (High automation 80-95%)
    'Regulatory-Compliance': {
        'description': 'Regulatory requirements and compliance analysis',
        'automation_potential': 0.88,
        'keywords': ['telemarketing sales rule', 'privacy policy', 'unfair tos',
                    'unfair terms', 'consumer protection', 'regulatory requirement',
                    'compliance check', 'regulation'],
        'examples': ['Regulatory compliance review', 'Privacy policy analysis', 'Consumer protection']
    },
    'Privacy-Policy-Analysis': {
        'description': 'Privacy policy interpretation and Q&A (OPP-115)',
        'automation_potential': 0.90,
        'keywords': ['opp-115', 'privacy policy qa', 'privacy policy entailment',
                    'data collection', 'user choice', 'first party use', 'third party sharing',
                    'data retention', 'data security', 'policy change', 'privacy'],
        'examples': ['Privacy policy review', 'Data practice analysis', 'Privacy compliance']
    },
    'Insurance-Policy': {
        'description': 'Insurance policy interpretation',
        'automation_potential': 0.83,
        'keywords': ['insurance policy', 'policy interpretation', 'coverage analysis',
                    'insurance claim', 'policy language', 'insurance terms'],
        'examples': ['Insurance policy review', 'Coverage determination', 'Policy interpretation']
    },
    
    # STATUTORY INTERPRETATION (Medium-High automation 75-85%)
    'Statutory-Interpretation': {
        'description': 'Textualism and statutory construction',
        'automation_potential': 0.78,
        'keywords': ['textualism', 'tool dictionaries', 'tool plain', 'statutory interpretation',
                    'statute', 'legislative intent', 'plain meaning', 'statutory construction'],
        'examples': ['Statute interpretation', 'Legislative analysis', 'Statutory meaning']
    },
    'Legal-Rule-Application': {
        'description': 'Applying legal rules to specific scenarios',
        'automation_potential': 0.82,
        'keywords': ['rule qa', 'abercrombie', 'hearsay', 'ucc v common law',
                    'successor liability', 'legal reasoning causality', 'apply rule',
                    'legal standard', 'legal test'],
        'examples': ['Rule application', 'Legal standard analysis', 'UCC analysis']
    },
    'Trademark-Law': {
        'description': 'Trademark distinctiveness analysis (Abercrombie)',
        'automation_potential': 0.80,
        'keywords': ['abercrombie', 'trademark', 'distinctiveness', 'generic', 'descriptive',
                    'suggestive', 'arbitrary', 'fanciful', 'trademark analysis'],
        'examples': ['Trademark classification', 'Distinctiveness analysis', 'Brand protection']
    },
    
    # EVIDENCE & DISCOVERY (High automation 85-92%)
    'Evidence-Analysis': {
        'description': 'Hearsay and evidence rules',
        'automation_potential': 0.85,
        'keywords': ['hearsay', 'evidence', 'admissibility', 'exception', 'testimonial',
                    'declaration', 'evidence rule', 'proof'],
        'examples': ['Hearsay analysis', 'Evidence admissibility', 'Evidentiary review']
    },
    'Document-Discovery': {
        'description': 'Document review and discovery analysis',
        'automation_potential': 0.92,
        'keywords': ['document production', 'discovery', 'responsive document', 'privilege',
                    'work product', 'review document', 'ediscovery', 'document analysis'],
        'examples': ['Discovery document review', 'Privilege review', 'Document production']
    },
    
    # SPECIALIZED LEGAL DOMAINS (Medium automation 70-85%)
    'Tax-Law': {
        'description': 'Tax court outcomes and tax law analysis',
        'automation_potential': 0.73,
        'keywords': ['canada tax court', 'tax court outcomes', 'tax law', 'tax analysis',
                    'tax dispute', 'tax assessment', 'tax ruling'],
        'examples': ['Tax case analysis', 'Tax outcome prediction', 'Tax law research']
    },
    'International-Law': {
        'description': 'International citizenship and cross-border legal questions',
        'automation_potential': 0.85,
        'keywords': ['international citizenship', 'citizenship questions', 'immigration',
                    'nationality', 'cross-border', 'international law'],
        'examples': ['Citizenship law analysis', 'Immigration questions', 'International legal research']
    },
    'Employment-Law': {
        'description': 'Employment contracts and non-compete analysis',
        'automation_potential': 0.80,
        'keywords': ['solicit of employees', 'solicit of customers', 'employment',
                    'non-compete', 'non-solicitation', 'employee agreement', 'restrictive covenant'],
        'examples': ['Employment contract review', 'Non-compete analysis', 'Solicitation restrictions']
    },
    'Ethics-Professional': {
        'description': 'Legal ethics and professional responsibility',
        'automation_potential': 0.70,
        'keywords': ['nys judicial ethics', 'judicial ethics', 'professional responsibility',
                    'ethics rules', 'conflict of interest', 'attorney ethics'],
        'examples': ['Ethics analysis', 'Conflict checking', 'Professional conduct review']
    },
    
    # LEGAL REASONING & ANALYSIS (Medium automation 65-80%)
    'Legal-Reasoning': {
        'description': 'Causality and legal reasoning patterns',
        'automation_potential': 0.75,
        'keywords': ['legal reasoning causality', 'intra rule distinguishing',
                    'legal analysis', 'reasoning', 'distinguish cases', 'analogize'],
        'examples': ['Legal reasoning analysis', 'Case distinction', 'Analogical reasoning']
    },
    'Definition-Extraction': {
        'description': 'Extracting and classifying legal definitions',
        'automation_potential': 0.88,
        'keywords': ['definition extraction', 'definition classification', 'defined term',
                    'legal definition', 'term meaning', 'glossary'],
        'examples': ['Definition extraction', 'Term identification', 'Glossary creation']
    },
    'Legal-Entailment': {
        'description': 'SARA entailment and logical inference',
        'automation_potential': 0.80,
        'keywords': ['sara entailment', 'sara numeric', 'logical inference', 'entailment',
                    'legal implication', 'follows from'],
        'examples': ['Statutory entailment', 'Logical analysis', 'Inference tasks']
    },
    
    # CORPORATE ACTIONS & DEALS (Medium-High automation 75-85%)
    'Deal-Structure': {
        'description': 'Deal structure and agreement terms',
        'automation_potential': 0.78,
        'keywords': ['jcrew blocker', 'termination services', 'agreement possession',
                    'consistent with past practice', 'occur after signing', 'deal structure',
                    'transaction structure'],
        'examples': ['Deal structure analysis', 'Transaction term review', 'Agreement structuring']
    },
    'Financial-Impact': {
        'description': 'Disproportionate impact and financial analysis',
        'automation_potential': 0.72,
        'keywords': ['disproportionate impact', 'financial impact', 'material adverse',
                    'financial analysis', 'impact assessment'],
        'examples': ['Financial impact analysis', 'Material adverse effect', 'Impact assessment']
    },
    'Private-Rights': {
        'description': 'Private right of action analysis',
        'automation_potential': 0.77,
        'keywords': ['proa', 'private right of action', 'standing', 'cause of action',
                    'statutory right', 'enforcement mechanism'],
        'examples': ['Private right analysis', 'Standing determination', 'Enforcement review']
    },
    
    # DOCUMENT PROCESSING (Very High automation 90-95%)
    'Document-Classification': {
        'description': 'Automated document classification and routing',
        'automation_potential': 0.93,
        'keywords': ['classify', 'categorize', 'document type', 'filing', 'organize',
                    'sort documents', 'document management', 'routing'],
        'examples': ['Document classification', 'File organization', 'Document routing']
    },
    'Form-Completion': {
        'description': 'Automated form filling and template completion',
        'automation_potential': 0.95,
        'keywords': ['form', 'fill out', 'complete form', 'template', 'standardized',
                    'form completion', 'data entry', 'populate'],
        'examples': ['Form automation', 'Template completion', 'Data population']
    },
    'Legal-Research': {
        'description': 'General legal research and information retrieval',
        'automation_potential': 0.90,
        'keywords': ['research', 'find', 'search', 'locate', 'legal research',
                    'case search', 'statute search', 'secondary source', 'treatise'],
        'examples': ['Legal research', 'Case law search', 'Statute research']
    },
    
    # ADMINISTRATIVE & ROUTINE (Very High automation 92-98%)
    'Calendar-Deadlines': {
        'description': 'Calendar management and deadline tracking',
        'automation_potential': 0.96,
        'keywords': ['calendar', 'deadline', 'docket', 'schedule', 'date',
                    'hearing date', 'filing deadline', 'statute of limitations'],
        'examples': ['Deadline tracking', 'Calendar management', 'Docket control']
    },
    'Filing-Service': {
        'description': 'Court filing and document service',
        'automation_potential': 0.94,
        'keywords': ['file', 'filing', 'serve', 'service', 'efiling', 'electronic filing',
                    'court filing', 'submit'],
        'examples': ['E-filing', 'Document filing', 'Service of process']
    },
    'Time-Billing': {
        'description': 'Time entry and billing tasks',
        'automation_potential': 0.92,
        'keywords': ['time entry', 'billing', 'invoice', 'billable', 'hourly',
                    'time tracking', 'matter', 'client billing'],
        'examples': ['Time tracking', 'Billing preparation', 'Invoice generation']
    },
    
    # DRAFTING & WRITING (Lower-Medium automation 55-75%)
    'Brief-Drafting': {
        'description': 'Legal brief and memorandum drafting',
        'automation_potential': 0.58,
        'keywords': ['draft brief', 'memorandum', 'motion', 'opposition', 'reply',
                    'brief', 'legal writing', 'argument'],
        'examples': ['Motion drafting', 'Brief preparation', 'Legal memoranda']
    },
    'Contract-Drafting': {
        'description': 'Contract and agreement drafting',
        'automation_potential': 0.65,
        'keywords': ['draft contract', 'draft agreement', 'prepare contract', 'new agreement',
                    'create contract', 'contract preparation'],
        'examples': ['Contract creation', 'Agreement drafting', 'Document preparation']
    },
    'Client-Communication': {
        'description': 'Client correspondence and communications',
        'automation_potential': 0.55,
        'keywords': ['email client', 'client communication', 'correspondence', 'letter',
                    'client update', 'status update', 'client call'],
        'examples': ['Client emails', 'Status updates', 'Client correspondence']
    }
}

@st.cache_data
def load_data(csv_path):
    """Load and preprocess the CSV data"""
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    
    # Convert hours to numeric
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')
    
    # Fill NaN hours with 0
    df['Hours'] = df['Hours'].fillna(0)
    
    # Extract year and month
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    df['Quarter'] = df['Date'].dt.quarter
    
    return df

def classify_task(description):
    """Classify a task description into LegalBench categories"""
    if pd.isna(description):
        return 'Unclassified', 0.0
    
    description_lower = description.lower()
    
    # Score each category
    scores = {}
    for category, info in LEGALBENCH_TASKS.items():
        score = sum(1 for keyword in info['keywords'] if keyword in description_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        best_category = max(scores, key=scores.get)
        automation_potential = LEGALBENCH_TASKS[best_category]['automation_potential']
        return best_category, automation_potential
    else:
        return 'Unclassified', 0.3

def extract_keywords(descriptions):
    """Extract common keywords from descriptions"""
    all_words = []
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 're', 'from', 'by', 'as', 'is', 'was', 'be', 'been',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                  'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
    
    for desc in descriptions:
        if pd.notna(desc):
            words = re.findall(r'\b[a-z]{4,}\b', desc.lower())
            all_words.extend([w for w in words if w not in stop_words])
    
    return Counter(all_words).most_common(30)

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "AiSavings2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show input for password
    if "password_correct" not in st.session_state:
        st.markdown('<h1 class="main-header">⚖️ Legal AI Automation Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("### 🔐 Secure Access Required")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "Enter Password", 
                type="password", 
                on_change=password_entered, 
                key="password",
                help="Contact your administrator for access"
            )
            st.info("💡 This dashboard contains confidential firm data and automation analysis.")
        return False
    
    # Password not correct, show input + error
    elif not st.session_state["password_correct"]:
        st.markdown('<h1 class="main-header">⚖️ Legal AI Automation Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("### 🔐 Secure Access Required")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "Enter Password", 
                type="password", 
                on_change=password_entered, 
                key="password",
                help="Contact your administrator for access"
            )
            st.error("❌ Incorrect password. Please try again.")
        return False
    
    # Password correct
    else:
        return True

def main():
    # Check password first
    if not check_password():
        return
    
    st.markdown('<h1 class="main-header">⚖️ Legal AI Automation Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Scale Law Firm - AI-Powered Efficiency Analysis")
    
    # Sidebar with logout option
    st.sidebar.title("📊 Dashboard Controls")
    
    # Add logout button at the top of sidebar
    if st.sidebar.button("🚪 Logout", help="Log out of the dashboard"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Load data
    try:
        # Try the filename with spaces first (as uploaded)
        import os
        csv_path = None
        
        # Check for the file with spaces
        if os.path.exists('activities 2025-10-30 10-21-00.csv'):
            csv_path = 'activities 2025-10-30 10-21-00.csv'
        # Also check for underscore version
        elif os.path.exists('activities_2025-10-30_10-21-00.csv'):
            csv_path = 'activities_2025-10-30_10-21-00.csv'
        else:
            # List available files to help debug
            available_files = os.listdir('/mnt/user-data/uploads/')
            st.error(f"❌ CSV file not found. Available files: {', '.join(available_files)}")
            st.info("💡 Please ensure your CSV file is uploaded to /mnt/user-data/uploads/")
            return
        
        df = load_data(csv_path)
        st.sidebar.success(f"✅ Loaded {len(df):,} activities")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("💡 Make sure your CSV file is in /mnt/user-data/uploads/ directory")
        return
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    # Year filter
    years = sorted(df['Year'].dropna().unique())
    selected_years = st.sidebar.multiselect("Select Years", years, default=years)
    
    # User filter
    users = sorted(df['User'].dropna().unique())
    selected_users = st.sidebar.multiselect("Select Users", users, default=[])
    
    # Apply filters
    filtered_df = df[df['Year'].isin(selected_years)]
    if selected_users:
        filtered_df = filtered_df[filtered_df['User'].isin(selected_users)]
    
    # Classify tasks
    with st.spinner("🤖 Analyzing tasks for AI automation potential..."):
        filtered_df[['Task_Category', 'Automation_Potential']] = filtered_df['Description'].apply(
            lambda x: pd.Series(classify_task(x))
        )
    
    # Calculate automation hours
    filtered_df['Automatable_Hours'] = filtered_df['Hours'] * filtered_df['Automation_Potential']
    filtered_df['Manual_Hours'] = filtered_df['Hours'] - filtered_df['Automatable_Hours']
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "🤖 Automation Analysis", 
        "💰 Cost Savings", 
        "🔮 Predictions",
        "📚 Task Definitions"
    ])
    
    # TAB 1: Overview
    with tab1:
        st.header("Overview Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_hours = filtered_df['Hours'].sum()
        automatable_hours = filtered_df['Automatable_Hours'].sum()
        automation_rate = (automatable_hours / total_hours * 100) if total_hours > 0 else 0
        
        with col1:
            st.metric(
                label="Total Hours Logged",
                value=f"{total_hours:,.0f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Automatable Hours",
                value=f"{automatable_hours:,.0f}",
                delta=f"{automation_rate:.1f}% of total"
            )
        
        with col3:
            total_billable = filtered_df['Billable ($)'].apply(
                lambda x: float(x) if pd.notna(x) and str(x).strip() else 0
            ).sum()
            st.metric(
                label="Total Billable",
                value=f"${total_billable:,.0f}"
            )
        
        with col4:
            unique_matters = filtered_df['Matter number'].nunique()
            st.metric(
                label="Unique Matters",
                value=f"{unique_matters:,}"
            )
        
        st.markdown("---")
        
        # Time series
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Hours by Month")
            monthly_data = filtered_df.groupby(['Year', 'Month', 'Month_Name']).agg({
                'Hours': 'sum',
                'Automatable_Hours': 'sum'
            }).reset_index()
            monthly_data = monthly_data.sort_values(['Year', 'Month'])
            monthly_data['Period'] = monthly_data['Month_Name'] + ' ' + monthly_data['Year'].astype(str)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_data['Period'],
                y=monthly_data['Hours'],
                name='Total Hours',
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                x=monthly_data['Period'],
                y=monthly_data['Automatable_Hours'],
                name='Automatable Hours',
                marker_color='darkblue'
            ))
            fig.update_layout(
                barmode='overlay',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏢 Top 10 Users by Hours")
            user_hours = filtered_df.groupby('User').agg({
                'Hours': 'sum',
                'Automatable_Hours': 'sum'
            }).reset_index().sort_values('Hours', ascending=False).head(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=user_hours['User'],
                x=user_hours['Hours'],
                name='Total Hours',
                orientation='h',
                marker_color='lightcoral'
            ))
            fig.add_trace(go.Bar(
                y=user_hours['User'],
                x=user_hours['Automatable_Hours'],
                name='Automatable',
                orientation='h',
                marker_color='darkred'
            ))
            fig.update_layout(
                barmode='overlay',
                height=400,
                hovermode='y unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Automation Analysis
    with tab2:
        st.header("🤖 AI Automation Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Task Category Distribution")
            category_data = filtered_df.groupby('Task_Category').agg({
                'Hours': 'sum',
                'Automatable_Hours': 'sum'
            }).reset_index()
            category_data = category_data.sort_values('Hours', ascending=False)
            
            fig = px.bar(
                category_data,
                x='Task_Category',
                y=['Hours', 'Automatable_Hours'],
                title="Hours by Task Category",
                labels={'value': 'Hours', 'variable': 'Type'},
                barmode='group',
                color_discrete_map={'Hours': 'lightblue', 'Automatable_Hours': 'darkblue'}
            )
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Automation Potential")
            
            # Pie chart
            fig = px.pie(
                category_data,
                values='Hours',
                names='Task_Category',
                title='Task Distribution',
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Top automatable keywords
        st.subheader("🔑 Top Keywords in Automatable Tasks")
        
        high_automation_tasks = filtered_df[filtered_df['Automation_Potential'] > 0.7]
        keywords = extract_keywords(high_automation_tasks['Description'].dropna())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Most Frequent Terms")
            for i, (word, count) in enumerate(keywords[:10], 1):
                st.write(f"{i}. **{word}** ({count:,} times)")
        
        with col2:
            st.markdown("#### Medium Frequency")
            for i, (word, count) in enumerate(keywords[10:20], 11):
                st.write(f"{i}. **{word}** ({count:,} times)")
        
        with col3:
            st.markdown("#### Emerging Terms")
            for i, (word, count) in enumerate(keywords[20:30], 21):
                st.write(f"{i}. **{word}** ({count:,} times)")
        
        # Word cloud style visualization
        st.subheader("📊 Keyword Frequency Visualization")
        keywords_df = pd.DataFrame(keywords[:20], columns=['Keyword', 'Count'])
        fig = px.bar(
            keywords_df,
            x='Count',
            y='Keyword',
            orientation='h',
            title='Top 20 Keywords in Automatable Tasks',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: Cost Savings
    with tab3:
        st.header("💰 Potential Cost Savings with AI")
        
        # Assumptions
        st.subheader("⚙️ Assumptions & Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_hourly_rate = st.number_input(
                "Average Hourly Rate ($)",
                min_value=100,
                max_value=1000,
                value=500,
                step=50
            )
        
        with col2:
            ai_efficiency_gain = st.slider(
                "AI Efficiency Gain (%)",
                min_value=10,
                max_value=90,
                value=60,
                help="Percentage of time saved on automatable tasks"
            ) / 100
        
        with col3:
            ai_cost_per_hour = st.number_input(
                "AI Cost per Hour ($)",
                min_value=1,
                max_value=100,
                value=10,
                step=5,
                help="Estimated cost of AI tools per hour"
            )
        
        st.markdown("---")
        
        # Calculate savings
        hours_saved = automatable_hours * ai_efficiency_gain
        labor_cost_saved = hours_saved * avg_hourly_rate
        ai_cost = automatable_hours * ai_cost_per_hour
        net_savings = labor_cost_saved - ai_cost
        roi = (net_savings / ai_cost * 100) if ai_cost > 0 else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Hours Potentially Saved",
                value=f"{hours_saved:,.0f}",
                delta=f"{(hours_saved/total_hours*100):.1f}% of total"
            )
        
        with col2:
            st.metric(
                label="Labor Cost Savings",
                value=f"${labor_cost_saved:,.0f}"
            )
        
        with col3:
            st.metric(
                label="AI Implementation Cost",
                value=f"${ai_cost:,.0f}"
            )
        
        with col4:
            st.metric(
                label="Net Savings",
                value=f"${net_savings:,.0f}",
                delta=f"ROI: {roi:.0f}%"
            )
        
        st.markdown("---")
        
        # Savings breakdown by category
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💵 Savings by Task Category")
            
            category_savings = filtered_df.groupby('Task_Category').agg({
                'Automatable_Hours': 'sum'
            }).reset_index()
            
            category_savings['Hours_Saved'] = category_savings['Automatable_Hours'] * ai_efficiency_gain
            category_savings['Cost_Savings'] = category_savings['Hours_Saved'] * avg_hourly_rate
            category_savings = category_savings.sort_values('Cost_Savings', ascending=False)
            
            fig = px.bar(
                category_savings,
                x='Task_Category',
                y='Cost_Savings',
                title='Potential Savings by Category',
                labels={'Cost_Savings': 'Savings ($)'},
                color='Cost_Savings',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Cumulative Savings")
            
            # Monthly cumulative savings
            monthly_savings = filtered_df.groupby(['Year', 'Month']).agg({
                'Automatable_Hours': 'sum'
            }).reset_index()
            monthly_savings = monthly_savings.sort_values(['Year', 'Month'])
            monthly_savings['Hours_Saved'] = monthly_savings['Automatable_Hours'] * ai_efficiency_gain
            monthly_savings['Monthly_Savings'] = monthly_savings['Hours_Saved'] * avg_hourly_rate
            monthly_savings['Cumulative_Savings'] = monthly_savings['Monthly_Savings'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_savings.index,
                y=monthly_savings['Cumulative_Savings'],
                mode='lines+markers',
                name='Cumulative Savings',
                fill='tozeroy',
                line=dict(color='green', width=3)
            ))
            fig.update_layout(
                title='Cumulative Cost Savings Over Time',
                xaxis_title='Month',
                yaxis_title='Cumulative Savings ($)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top matters for automation
        st.subheader("🎯 Top Matters for AI Implementation")
        
        matter_analysis = filtered_df.groupby('Matter description').agg({
            'Hours': 'sum',
            'Automatable_Hours': 'sum'
        }).reset_index()
        matter_analysis['Automation_Rate'] = (
            matter_analysis['Automatable_Hours'] / matter_analysis['Hours'] * 100
        )
        matter_analysis['Potential_Savings'] = (
            matter_analysis['Automatable_Hours'] * ai_efficiency_gain * avg_hourly_rate
        )
        matter_analysis = matter_analysis.sort_values('Potential_Savings', ascending=False).head(15)
        
        st.dataframe(
            matter_analysis.style.format({
                'Hours': '{:.1f}',
                'Automatable_Hours': '{:.1f}',
                'Automation_Rate': '{:.1f}%',
                'Potential_Savings': '${:,.0f}'
            }),
            use_container_width=True,
            height=400
        )
    
    # TAB 4: Predictions
    with tab4:
        st.header("🔮 2025 Projections & Predictions")
        
        # Project full year based on current data
        current_data = filtered_df[filtered_df['Year'] == 2025]
        
        if len(current_data) > 0:
            # Get latest month with data
            latest_month = current_data['Month'].max()
            
            # Calculate monthly averages
            monthly_avg = current_data.groupby('Month').agg({
                'Hours': 'sum',
                'Automatable_Hours': 'sum'
            }).mean()
            
            # Project for remaining months
            months_elapsed = latest_month
            months_remaining = 12 - months_elapsed
            
            projected_total_hours = (current_data['Hours'].sum() + 
                                    monthly_avg['Hours'] * months_remaining)
            projected_automatable_hours = (current_data['Automatable_Hours'].sum() + 
                                          monthly_avg['Automatable_Hours'] * months_remaining)
            
            # Display projections
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Projected Total Hours (2025)",
                    value=f"{projected_total_hours:,.0f}",
                    delta=f"+{months_remaining} months projected"
                )
            
            with col2:
                st.metric(
                    label="Projected Automatable Hours",
                    value=f"{projected_automatable_hours:,.0f}",
                    delta=f"{(projected_automatable_hours/projected_total_hours*100):.1f}%"
                )
            
            with col3:
                projected_savings = projected_automatable_hours * ai_efficiency_gain * avg_hourly_rate
                st.metric(
                    label="Projected Annual Savings",
                    value=f"${projected_savings:,.0f}"
                )
            
            st.markdown("---")
            
            # Projection chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Monthly Projection")
                
                # Create projection data
                actual_monthly = current_data.groupby('Month').agg({
                    'Hours': 'sum',
                    'Automatable_Hours': 'sum'
                }).reset_index()
                
                # Create full year projection
                all_months = pd.DataFrame({'Month': range(1, 13)})
                projection_df = all_months.merge(actual_monthly, on='Month', how='left')
                
                # Fill projected values
                projection_df['Hours'] = projection_df['Hours'].fillna(monthly_avg['Hours'])
                projection_df['Automatable_Hours'] = projection_df['Automatable_Hours'].fillna(
                    monthly_avg['Automatable_Hours']
                )
                projection_df['Type'] = projection_df['Month'].apply(
                    lambda x: 'Actual' if x <= months_elapsed else 'Projected'
                )
                
                fig = go.Figure()
                
                # Actual data
                actual = projection_df[projection_df['Type'] == 'Actual']
                fig.add_trace(go.Bar(
                    x=actual['Month'],
                    y=actual['Hours'],
                    name='Actual Total',
                    marker_color='lightblue'
                ))
                fig.add_trace(go.Bar(
                    x=actual['Month'],
                    y=actual['Automatable_Hours'],
                    name='Actual Automatable',
                    marker_color='darkblue'
                ))
                
                # Projected data
                projected = projection_df[projection_df['Type'] == 'Projected']
                fig.add_trace(go.Bar(
                    x=projected['Month'],
                    y=projected['Hours'],
                    name='Projected Total',
                    marker_color='lightcoral',
                    opacity=0.6
                ))
                fig.add_trace(go.Bar(
                    x=projected['Month'],
                    y=projected['Automatable_Hours'],
                    name='Projected Automatable',
                    marker_color='darkred',
                    opacity=0.6
                ))
                
                fig.update_layout(
                    title='2025 Monthly Hours Projection',
                    xaxis_title='Month',
                    yaxis_title='Hours',
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("💰 Cumulative Savings Projection")
                
                projection_df['Monthly_Savings'] = (
                    projection_df['Automatable_Hours'] * ai_efficiency_gain * avg_hourly_rate
                )
                projection_df['Cumulative_Savings'] = projection_df['Monthly_Savings'].cumsum()
                
                fig = go.Figure()
                
                # Actual cumulative
                actual_cum = projection_df[projection_df['Type'] == 'Actual']
                fig.add_trace(go.Scatter(
                    x=actual_cum['Month'],
                    y=actual_cum['Cumulative_Savings'],
                    mode='lines+markers',
                    name='Actual',
                    line=dict(color='green', width=3),
                    fill='tozeroy'
                ))
                
                # Projected cumulative
                fig.add_trace(go.Scatter(
                    x=projection_df['Month'],
                    y=projection_df['Cumulative_Savings'],
                    mode='lines+markers',
                    name='Projected',
                    line=dict(color='lightgreen', width=3, dash='dash'),
                    fill='tozeroy',
                    opacity=0.5
                ))
                
                fig.update_layout(
                    title='Cumulative Savings Projection',
                    xaxis_title='Month',
                    yaxis_title='Cumulative Savings ($)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Scenario analysis
            st.markdown("---")
            st.subheader("🎲 Scenario Analysis")
            
            scenarios = {
                'Conservative (40% efficiency)': 0.40,
                'Moderate (60% efficiency)': 0.60,
                'Optimistic (80% efficiency)': 0.80
            }
            
            scenario_results = []
            for scenario_name, efficiency in scenarios.items():
                hours_saved = projected_automatable_hours * efficiency
                cost_saved = hours_saved * avg_hourly_rate
                ai_cost = projected_automatable_hours * ai_cost_per_hour
                net_savings = cost_saved - ai_cost
                
                scenario_results.append({
                    'Scenario': scenario_name,
                    'Hours Saved': hours_saved,
                    'Cost Saved': cost_saved,
                    'AI Cost': ai_cost,
                    'Net Savings': net_savings,
                    'ROI (%)': (net_savings / ai_cost * 100) if ai_cost > 0 else 0
                })
            
            scenario_df = pd.DataFrame(scenario_results)
            
            # Display scenarios
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=scenario_df['Scenario'],
                    y=scenario_df['Net Savings'],
                    name='Net Savings',
                    marker_color='green',
                    text=scenario_df['Net Savings'].apply(lambda x: f'${x:,.0f}'),
                    textposition='auto'
                ))
                
                fig.update_layout(
                    title='Net Savings by Scenario',
                    xaxis_title='Scenario',
                    yaxis_title='Net Savings ($)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    scenario_df.style.format({
                        'Hours Saved': '{:,.0f}',
                        'Cost Saved': '${:,.0f}',
                        'AI Cost': '${:,.0f}',
                        'Net Savings': '${:,.0f}',
                        'ROI (%)': '{:.0f}%'
                    }),
                    use_container_width=True,
                    height=400
                )
        else:
            st.warning("No 2025 data available for projections")
    
    # TAB 5: Task Definitions
    with tab5:
        st.header("📚 LegalBench Task Definitions")
        st.markdown("""
        Based on the **LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning 
        in Large Language Models**, here are the key task categories that can be automated with AI:
        """)
        
        for category, info in LEGALBENCH_TASKS.items():
            with st.expander(f"**{category}** - Automation Potential: {info['automation_potential']*100:.0f}%"):
                st.markdown(f"**Description:** {info['description']}")
                
                st.markdown("**Common Keywords:**")
                st.write(", ".join(info['keywords']))
                
                st.markdown("**Example Tasks:**")
                for example in info['examples']:
                    st.write(f"• {example}")
                
                # Show actual tasks from data
                matching_tasks = filtered_df[
                    filtered_df['Task_Category'] == category
                ]['Description'].value_counts().head(5)
                
                if len(matching_tasks) > 0:
                    st.markdown("**Top 5 Actual Tasks in Your Data:**")
                    for task, count in matching_tasks.items():
                        if pd.notna(task):
                            st.write(f"• {task[:100]}{'...' if len(task) > 100 else ''} ({count} times)")
        
        st.markdown("---")
        st.subheader("📊 Automation Potential Summary")
        
        summary_df = pd.DataFrame([
            {
                'Category': cat,
                'Automation Potential': f"{info['automation_potential']*100:.0f}%",
                'Primary Use Cases': ', '.join(info['examples'][:2])
            }
            for cat, info in LEGALBENCH_TASKS.items()
        ])
        
        st.dataframe(summary_df, use_container_width=True, height=400)
        
        # Implementation recommendations
        st.markdown("---")
        st.subheader("💡 Implementation Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Quick Wins (High Automation Potential)
            1. **Document Review** (90%) - Implement AI-powered contract review
            2. **Rule-Recall/Legal Research** (95%) - AI legal research assistants
            3. **Routine Administrative** (95%) - Automated form filling and filing
            4. **Issue-Spotting** (85%) - AI-assisted initial case assessment
            """)
        
        with col2:
            st.markdown("""
            #### Medium-Term Opportunities
            1. **Interpretation** (80%) - Contract clause analysis tools
            2. **Rule-Application** (70%) - Compliance assessment automation
            3. **Rule-Conclusion** (65%) - AI-assisted legal opinions
            4. **Rhetorical Understanding** (55%) - Assisted brief drafting
            """)
        
        st.info("""
        **Note:** The automation potentials are estimates based on current AI capabilities and 
        the LegalBench framework. Actual results may vary based on specific use cases, 
        implementation quality, and human oversight requirements.
        """)

if __name__ == "__main__":
    main()
