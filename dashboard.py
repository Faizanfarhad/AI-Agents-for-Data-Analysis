import streamlit as st
from agent import Agent
from data_visualizer import AutoDataVisualizer
import os
from pathlib import Path as p
import pandas as pd 

# --- page configuration ------------------------------------------------------
st.set_page_config(
    page_title="AI Agent For Data Analysis",
    page_icon="🤖",             # show robot icon in browser tab
    layout="wide",
    initial_sidebar_state="expanded",
)

# simple CSS tweaks (hide default menu/footer, add custom footer later)
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""


files = list(p.cwd().joinpath('cleanedDF').glob('*'))
files_ = list(p.cwd().joinpath('UserInputFiles').glob('*'))


def clean_previous_file():
        for root,dir,files in os.walk('cleanedDF'):
                for curr_file in files:
                        if curr_file.endswith('.csv') or curr_file.endswith('.json') or curr_file.endswith('.txt'):
                                os.remove('cleanedDF/' +curr_file)

def fetch_cleanedfile(filetype: str):
        """Fetch cleaned file from cleanedDF folder"""
        for root, dir, files in os.walk('cleanedDF'):
                if files and files[0].endswith(filetype):
                        return files[0]
        return None

def saveFile_getPath(infile):
        """Save uploaded file and return path"""
        if infile is not None:
                save_path = os.path.join("UserInputFiles", infile.name)
                with open(save_path, 'wb') as f:
                        f.write(infile.getbuffer())
                st.success(f'✅ File saved to: {save_path}')
                return save_path
        return None

def get_param():
        """Get user parameters"""
        model_provider = 'google_genai'
        model_name = st.multiselect(
                label='Select a model:',
                options=["gemini-2.5-flash-lite"]
        )
        if isinstance(model_name, list) and model_name:
                model_name = model_name[0]
        else:
                model_name = None
                
        input_file = st.file_uploader(
                label="Upload Dataset:",
                type=['json', 'csv', 'xlsx', 'text']
        )
        api = st.text_input(label="Enter your API key:", type='password')
        
        input_file = saveFile_getPath(input_file)
        return model_name, model_provider, input_file, api


# ============= MAIN DASHBOARD =============
st.title("🤖 AI Agent For Data Analysis & Auto Visualizer")


st.markdown("""
This application:
- 📊 Automatically analyzes and visualizes datasets
- 🧹 Preprocesses data by cleaning and validation
- 🤖 Uses AI agents to provide insights
- ✋ Does not store your data or API keys
""")


# ============= SIDEBAR - INPUT PARAMETERS =============
with st.sidebar:
        st.header("⚙️ Configuration")
        model_name, model_provider, input_file, api = get_param()

# ============= SECTION 1: AUTO VISUALIZER (No Agent Needed) =============
st.divider()
st.header("📊 Auto Data Visualizer")

st.markdown("**No AI Agent needed!** Upload a CSV file directly to visualize it automatically:")

uploaded_file = st.file_uploader(
        label="📁 Upload CSV for Direct Visualization:",
        type=['csv'],
        key='direct_upload'
)

if uploaded_file is not None:
        try:
                df_viz = pd.read_csv(uploaded_file)
                
                with st.spinner('🔍 Analyzing dataset...'):
                        visualizer = AutoDataVisualizer(df_viz)
                        summary = visualizer.get_data_summary()
                        insights = visualizer.generate_insights()
                
                # Display summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                        st.metric("Rows", summary['shape'][0])
                with col2:
                        st.metric("Columns", summary['shape'][1])
                with col3:
                        st.metric("Numeric", summary['numeric_columns'])
                with col4:
                        st.metric("Categorical", summary['categorical_columns'])
                
                # Display insights
                st.subheader("📈 Dataset Insights")
                for insight in insights:
                        st.info(insight)
                
                # Generate visualizations
                st.subheader("📉 Visualizations")
                dashboard_data = visualizer.generate_dashboard_data()
                
                # Missing data
                if dashboard_data['missing_data']:
                        st.plotly_chart(dashboard_data['missing_data'], use_container_width=True)
                
                # Numeric distributions
                if dashboard_data['numeric_dist']:
                        st.subheader("📊 Numeric Distributions")
                        st.plotly_chart(dashboard_data['numeric_dist'], use_container_width=True)
                
                # Categorical distributions
                if dashboard_data['categorical_dist']:
                        st.subheader("🏷️ Categorical Distributions")
                        st.plotly_chart(dashboard_data['categorical_dist'], use_container_width=True)
                
                # Correlations
                if dashboard_data['correlations']:
                        st.subheader("🔗 Correlation Matrix")
                        st.plotly_chart(dashboard_data['correlations'], use_container_width=True)
                
                # Numeric relationships
                if dashboard_data['numeric_relationships']:
                        st.subheader("📐 Numeric Variables Relationships")
                        st.plotly_chart(dashboard_data['numeric_relationships'], use_container_width=True)
                
                # Categorical-Numeric relationships
                if dashboard_data['cat_num_relationships']:
                        st.subheader("📊 Categorical vs Numeric Analysis")
                        st.plotly_chart(dashboard_data['cat_num_relationships'], use_container_width=True)
                
                # Display raw data
                with st.expander("👀 View Raw Data"):
                        st.dataframe(df_viz, use_container_width=True)
                        st.download_button(
                                label="⬇️ Download Visualization Summary",
                                data=df_viz.describe().to_csv(),
                                file_name="data_summary.csv"
                        )
                
        except Exception as e:
                st.error(f"❌ Error analyzing file: {str(e)}")

# ============= SECTION 2: AI AGENT PROCESSING =============
st.divider()
st.header("🤖 AI Agent Processing (Optional)")

if model_name and api and input_file:
        st.success(f"✅ Ready to process using {model_name}!")
        
        if st.button("🚀 Run AI Agent", key="run_agent"):
                try:
                        #NOTE : cleaning previous files before calling current file
                        clean_previous_file()
                        
                        with st.spinner("⏳ Processing dataset with AI Agent..."):
                                agent = Agent(
                                        model_name=model_name,
                                        model_provider=model_provider,
                                        input_source=input_file,
                                        api_key=api
                                )
                                result = agent.run()
                                st.success(f"✅ Agent execution completed: {result}")
                        
                        # Load and visualize cleaned data
                        file_name = fetch_cleanedfile('.csv')
                        if file_name:
                                st.subheader("📊 Cleaned Data Visualization")
                                df_cleaned = pd.read_csv("cleanedDF/" + file_name)
                                
                                with st.spinner('🔍 Analyzing cleaned dataset...'):
                                        visualizer = AutoDataVisualizer(df_cleaned)
                                        dashboard_data = visualizer.generate_dashboard_data()
                                
                                if dashboard_data['numeric_dist']:
                                        st.plotly_chart(dashboard_data['numeric_dist'], use_container_width=True)
                                
                                if dashboard_data['categorical_dist']:
                                        st.plotly_chart(dashboard_data['categorical_dist'], use_container_width=True)
                                
                                if dashboard_data['correlations']:
                                        st.plotly_chart(dashboard_data['correlations'], use_container_width=True)
                                
                except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
else:
        st.warning("⚠️ Please select a model, upload a file, and enter your API key to use the AI Agent.")


