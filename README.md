# Legal AI Automation Dashboard

A comprehensive Streamlit dashboard for analyzing legal work activities and predicting automation opportunities using AI, based on the LegalBench framework.

## 🎯 Features

### 1. **Overview Dashboard** 📈
- Total hours logged and automation statistics
- Monthly trends and patterns
- Top users by billable hours
- Matter distribution analysis

### 2. **Automation Analysis** 🤖
- Task categorization using comprehensive LegalBench framework
- **37 task categories** covering **162+ individual tasks** with automation potential ratings:
  
  **Very High Automation (90-96%):**
  - Form-Completion (95%)
  - Calendar-Deadlines (96%)
  - Filing-Service (94%)
  - Document-Classification (93%)
  - Time-Billing (92%)
  - Contract-Clause-Identification (92%) - 41 CUAD tasks
  - Document-Discovery (92%)
  - Privacy-Policy-Analysis (90%) - 23 OPP-115 tasks
  - Case-Law-Analysis (90%)
  - Legal-Research (90%)
  
  **High Automation (80-89%):**
  - Contract-NLI-Analysis (88%) - 15+ tasks
  - Definition-Extraction (88%)
  - Regulatory-Compliance (88%)
  - Litigation-Documents (87%)
  - Legal-Issue-Spotting (85%) - 13 Learned Hands tasks
  - Contract-QA (85%)
  - Evidence-Analysis (85%)
  - International-Law (85%)
  - Insurance-Policy (83%)
  - M&A-Deal-Terms (82%) - 27+ MAUD tasks
  - Legal-Rule-Application (82%)
  - Legal-Entailment (80%)
  - Corporate-Transactions (80%)
  - Trademark-Law (80%)
  - Employment-Law (80%)
  
  **Medium Automation (70-79%):**
  - Statutory-Interpretation (78%) - 3 Textualism tasks
  - Deal-Structure (78%)
  - Private-Rights (77%)
  - Legal-Reasoning (75%)
  - Procedural-Analysis (75%)
  - Corporate-Governance (75%)
  - Tax-Law (73%)
  - Financial-Impact (72%)
  - Ethics-Professional (70%)
  
  **Lower Automation (55-69%):**
  - Contract-Drafting (65%)
  - Brief-Drafting (58%)
  - Client-Communication (55%)

- Real-time keyword extraction and frequency analysis
- Intelligent task classification using 500+ keywords
- Practice area distribution analysis

### 3. **Cost Savings Analysis** 💰
- Customizable parameters (hourly rates, efficiency gains, AI costs)
- Real-time ROI calculations
- Savings breakdown by task category
- Top matters for AI implementation
- Cumulative savings visualization

### 4. **2025 Projections** 🔮
- Full-year projections based on current data
- Monthly forecast visualization
- Scenario analysis (Conservative, Moderate, Optimistic)
- Projected annual savings calculations

### 5. **Task Definitions** 📚
- Detailed LegalBench task category definitions
- Automation potential ratings
- Example use cases
- Real examples from your data
- Implementation recommendations

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Dashboard

1. **Make sure your data files are in the correct location:**
   - CSV file: `/mnt/user-data/uploads/activities_2025-10-30_10-21-00.csv`
   - PDF file: `/mnt/user-data/uploads/legalbench.pdf`

2. **Run the Streamlit app:**
```bash
streamlit run legal_ai_automation_dashboard.py
```

3. **Login to the dashboard:**
   - **Password**: `AiSavings2025`
   - The password protects confidential firm data
   - You can logout using the button in the sidebar

4. **The dashboard will open in your browser at:** `http://localhost:8501`

## 🔐 Security Features

### Password Protection
- The dashboard requires password authentication on first access
- **Default Password**: `AiSavings2025`
- Password is session-based (remains active during your session)
- Use the "Logout" button in the sidebar to end your session
- Password prevents unauthorized access to sensitive firm data

### Changing the Password
To change the password, edit line in `legal_ai_automation_dashboard.py`:
```python
if st.session_state["password"] == "AiSavings2025":  # Change this password
```

## 📚 Comprehensive Task Reference

See **[LEGALBENCH_TASKS_REFERENCE.md](LEGALBENCH_TASKS_REFERENCE.md)** for:
- Complete list of all 162+ LegalBench tasks
- Detailed descriptions of all 37 categories
- Individual task breakdowns (CUAD, MAUD, OPP-115, Learned Hands, etc.)
- Implementation priority matrix
- ROI estimation by category
- Specific automation strategies for each task type

---

## 📊 Dashboard Controls

### Filters (Sidebar)
- **Year Selection**: Filter data by specific years
- **User Selection**: Analyze specific attorneys or all users
- **Real-time Updates**: All charts and metrics update based on filters

### Customizable Parameters (Cost Savings Tab)
- **Average Hourly Rate**: Set your firm's average billing rate ($100-$1000)
- **AI Efficiency Gain**: Adjust expected time savings (10-90%)
- **AI Cost per Hour**: Set estimated AI tool costs ($1-$100)

## 📈 Understanding the Metrics

### Key Metrics
- **Total Hours Logged**: Sum of all time entries
- **Automatable Hours**: Hours that can potentially be automated with AI
- **Automation Rate**: Percentage of work that can be automated
- **Total Billable**: Total billable amount from activities
- **Unique Matters**: Number of distinct client matters

### Automation Potential
Each task is classified into one of 8 categories based on:
- **Keywords** in the task description
- **LegalBench framework** alignment
- **Predefined automation potential** ratings

### Cost Calculations
- **Labor Cost Savings** = Automatable Hours × Efficiency Gain × Hourly Rate
- **AI Implementation Cost** = Automatable Hours × AI Cost per Hour
- **Net Savings** = Labor Cost Savings - AI Implementation Cost
- **ROI** = (Net Savings / AI Implementation Cost) × 100

## 🎯 Use Cases

### For Managing Partners
- Understand total automation potential across the firm
- Identify high-value matters for AI implementation
- Calculate expected ROI and cost savings
- Make data-driven decisions about AI investments

### For Practice Group Leaders
- Analyze which types of work can be automated
- Identify efficiency opportunities in your group
- Plan resource allocation and training needs

### For Operations/Innovation Teams
- Prioritize AI tool implementation
- Track automation progress over time
- Justify AI investments with concrete projections
- Identify quick wins vs. long-term opportunities

## 🔍 Task Categories Explained

### High Automation Potential (80-95%)
1. **Routine-Administrative** (95%): Filing, scheduling, form completion
2. **Rule-Recall** (95%): Legal research, citation checking
3. **Document-Review** (90%): Discovery, due diligence, contract review
4. **Issue-Spotting** (85%): Initial case assessment, conflict checks

### Medium Automation Potential (65-80%)
5. **Interpretation** (80%): Contract clause analysis, policy review
6. **Rule-Application** (70%): Compliance assessment, regulatory analysis
7. **Rule-Conclusion** (65%): Risk assessment, basic legal opinions

### Lower Automation Potential (50-65%)
8. **Rhetorical-Understanding** (55%): Brief drafting, persuasive writing

## 📝 Data Requirements

### CSV File Format
Required columns:
- `Date`: MM/DD/YYYY format
- `Hours`: Numeric hours worked
- `Description`: Text description of the activity
- `User`: Attorney/staff name
- `Matter number`: Unique matter identifier
- `Matter description`: Description of the matter
- `Billable ($)`: Billable amount (optional)

### Sample Data Structure
```csv
Type,Date,Hours,Description,Matter number,Matter description,User,Billable ($)
TimeEntry,01/01/2025,2.0,Review contract terms,12345,General Business,John Doe,1000.0
```

## 🔧 Customization

### Adding New Task Categories
Edit the `LEGALBENCH_TASKS` dictionary in the code:
```python
LEGALBENCH_TASKS = {
    'Your-Category': {
        'description': 'Description of the task type',
        'automation_potential': 0.85,  # 0.0 to 1.0
        'keywords': ['keyword1', 'keyword2'],
        'examples': ['Example 1', 'Example 2']
    }
}
```

### Modifying Automation Potential
Adjust the `automation_potential` values (0.0-1.0) based on your firm's experience with AI tools.

## 💡 Tips for Best Results

1. **Data Quality**: Ensure consistent description formats for better categorization
2. **Regular Updates**: Update the CSV monthly to track trends
3. **Filter Usage**: Use filters to analyze specific practice groups or time periods
4. **Scenario Testing**: Try different efficiency gain percentages in the Cost Savings tab
5. **Keyword Review**: Check the keyword analysis to refine task descriptions

## 🛠️ Troubleshooting

### Common Issues

**Dashboard won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python 3.8+ is installed

**Can't login:**
- Default password is: `AiSavings2025` (case-sensitive)
- Clear your browser cache if password keeps failing
- Check that you're entering the password correctly

**Data not loading:**
- Verify CSV file path is correct
- Check CSV encoding (should be UTF-8)
- Ensure date format is MM/DD/YYYY

**Incorrect categorization:**
- Review task descriptions for clarity
- Add more specific keywords to task descriptions
- Customize the `LEGALBENCH_TASKS` dictionary

**Session/Logout issues:**
- Click the "Logout" button in the sidebar
- Refresh the browser page
- Clear browser cookies if needed

## 📚 About LegalBench

This dashboard is based on the LegalBench framework, a collaboratively built benchmark for measuring legal reasoning in Large Language Models. The framework identifies six core types of legal reasoning:

1. **Issue-Spotting**: Identifying relevant legal issues
2. **Rule-Recall**: Recalling legal rules and precedents
3. **Rule-Application**: Applying rules to facts
4. **Rule-Conclusion**: Drawing conclusions from rule application
5. **Interpretation**: Interpreting legal language
6. **Rhetorical-Understanding**: Understanding persuasive elements

The dashboard extends this with additional practical categories relevant to law firm operations.

## 📞 Support

For issues or questions about the dashboard:
1. Check this README for troubleshooting tips
2. Review the Task Definitions tab for category explanations
3. Ensure your data matches the required format

## 🔒 Data Privacy

- All data processing happens locally
- No data is sent to external servers
- Review your firm's data policies before sharing results

## 📄 License

This dashboard is provided as-is for internal use at Scale Law Firm.

---

**Version**: 1.0  
**Last Updated**: October 2024  
**Compatible with**: Streamlit 1.28+, Python 3.8+
