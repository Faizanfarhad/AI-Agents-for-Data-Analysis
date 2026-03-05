"""
AutoDataVisualizer: Automatically analyze and visualize datasets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class AutoDataVisualizer:
    """
    Automatically detects data types and generates appropriate visualizations
    """
    
    def __init__(self, df: pd.DataFrame, sample_size: int = 5000):
        """
        Initialize the visualizer with a dataframe
        
        Args:
            df: Pandas DataFrame to visualize
            sample_size: Number of rows to use for analysis (for large datasets)
        """
        self.df = df.sample(n=min(sample_size, len(df))) if len(df) > sample_size else df
        self.original_df = df
        self.numeric_cols = []
        self.categorical_cols = []
        self.datetime_cols = []
        self.analyze_columns()
        
    def analyze_columns(self):
        """Analyze and categorize columns by type"""
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.numeric_cols.append(col)
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.datetime_cols.append(col)
            else:
                self.categorical_cols.append(col)
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics of the dataset"""
        return {
            'shape': self.original_df.shape,
            'numeric_columns': len(self.numeric_cols),
            'categorical_columns': len(self.categorical_cols),
            'datetime_columns': len(self.datetime_cols),
            'missing_values': self.original_df.isnull().sum().to_dict(),
        }
    
    def plot_numeric_distributions(self, max_cols: int = 6) -> go.Figure:
        """
        Create histograms for numeric columns
        
        Args:
            max_cols: Maximum number of columns to display
            
        Returns:
            Plotly figure
        """
        if not self.numeric_cols:
            return None
        
        cols_to_plot = self.numeric_cols[:max_cols]
        n_cols = len(cols_to_plot)
        n_rows = (n_cols + 2) // 3
        
        fig = make_subplots(
            rows=n_rows, cols=3,
            subplot_titles=cols_to_plot,
            specs=[[{'type': 'histogram'} for _ in range(3)] for _ in range(n_rows)]
        )
        
        for idx, col in enumerate(cols_to_plot):
            row = (idx // 3) + 1
            col_pos = (idx % 3) + 1
            
            fig.add_trace(
                go.Histogram(x=self.df[col], name=col, nbinsx=30),
                row=row, col=col_pos
            )
        
        fig.update_layout(height=300*n_rows, showlegend=False, title_text="Numeric Distributions")
        return fig
    
    def plot_categorical_distributions(self, max_cols: int = 6, top_n: int = 10) -> go.Figure:
        """
        Create bar charts for categorical columns
        
        Args:
            max_cols: Maximum number of columns to display
            top_n: Top N categories to show
            
        Returns:
            Plotly figure
        """
        if not self.categorical_cols:
            return None
        
        cols_to_plot = self.categorical_cols[:max_cols]
        n_cols = len(cols_to_plot)
        n_rows = (n_cols + 2) // 3
        
        fig = make_subplots(
            rows=n_rows, cols=3,
            subplot_titles=cols_to_plot,
            specs=[[{'type': 'bar'} for _ in range(3)] for _ in range(n_rows)]
        )
        
        for idx, col in enumerate(cols_to_plot):
            row = (idx // 3) + 1
            col_pos = (idx % 3) + 1
            
            value_counts = self.df[col].value_counts().head(top_n)
            
            fig.add_trace(
                go.Bar(x=value_counts.index.astype(str), y=value_counts.values, name=col),
                row=row, col=col_pos
            )
        
        fig.update_layout(height=300*n_rows, showlegend=False, title_text="Categorical Distributions")
        return fig
    
    def plot_correlations(self) -> Optional[go.Figure]:
        """
        Create correlation heatmap for numeric columns
        
        Returns:
            Plotly figure or None if less than 2 numeric columns
        """
        if len(self.numeric_cols) < 2:
            return None
        
        corr_matrix = self.df[self.numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Correlation Matrix",
            height=500,
            width=500,
        )
        return fig
    
    def plot_missing_data(self) -> go.Figure:
        """
        Visualize missing data
        
        Returns:
            Plotly figure
        """
        missing = self.original_df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        
        if len(missing) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No missing values in dataset!")
            return fig
        
        fig = go.Figure(data=[
            go.Bar(x=missing.index, y=missing.values, marker_color='indianred')
        ])
        
        fig.update_layout(
            title="Missing Values Count",
            xaxis_title="Columns",
            yaxis_title="Count",
            height=400
        )
        return fig
    
    def plot_numeric_relationships(self) -> Optional[go.Figure]:
        """
        Create scatter plot matrix for numeric columns (up to 4)
        
        Returns:
            Plotly figure or None
        """
        if len(self.numeric_cols) < 2:
            return None
        
        cols_to_plot = self.numeric_cols[:4]
        
        fig = px.scatter_matrix(
            self.df[cols_to_plot],
            dimensions=cols_to_plot,
            title="Numeric Variables Relationships",
            height=600,
            width=800
        )
        
        fig.update_traces(diagonal_visible=False)
        return fig
    
    def plot_categorical_numeric_relationships(self) -> Optional[go.Figure]:
        """
        Create box plots showing relationship between categorical and numeric variables
        
        Returns:
            Plotly figure or None
        """
        if not self.categorical_cols or not self.numeric_cols:
            return None
        
        cat_col = self.categorical_cols[0]
        num_cols = self.numeric_cols[:3]
        n_cols = len(num_cols)
        
        fig = make_subplots(
            rows=1, cols=n_cols,
            subplot_titles=num_cols,
            specs=[[{'type': 'box'} for _ in range(n_cols)]]
        )
        
        # Limit categories to top 10 to avoid overcrowding
        top_cats = self.df[cat_col].value_counts().head(10).index
        filtered_df = self.df[self.df[cat_col].isin(top_cats)]
        
        for idx, num_col in enumerate(num_cols):
            for cat in top_cats:
                data = filtered_df[filtered_df[cat_col] == cat][num_col]
                fig.add_trace(
                    go.Box(y=data, name=str(cat)),
                    row=1, col=idx+1
                )
        
        fig.update_layout(
            title=f"Relationship between {cat_col} and Numeric Variables",
            height=400,
            showlegend=True
        )
        return fig
    
    def generate_dashboard_data(self) -> Dict:
        """
        Generate all visualization data at once
        
        Returns:
            Dictionary containing all visualizations
        """
        dashboard_data = {
            'summary': self.get_data_summary(),
            'numeric_dist': self.plot_numeric_distributions(),
            'categorical_dist': self.plot_categorical_distributions(),
            'correlations': self.plot_correlations(),
            'missing_data': self.plot_missing_data(),
            'numeric_relationships': self.plot_numeric_relationships(),
            'cat_num_relationships': self.plot_categorical_numeric_relationships(),
        }
        return dashboard_data
    
    def generate_insights(self) -> List[str]:
        """
        Generate basic insights about the dataset
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Check for missing data
        missing_pct = (self.original_df.isnull().sum() / len(self.original_df) * 100).max()
        if missing_pct > 50:
            insights.append(f"⚠️ Dataset has significant missing values (up to {missing_pct:.1f}%)")
        elif missing_pct > 0:
            insights.append(f"ℹ️ Dataset has {missing_pct:.1f}% missing values")
        else:
            insights.append("✅ No missing values found")
        
        # Check for imbalanced categories
        if self.categorical_cols:
            for col in self.categorical_cols[:3]:
                unique_val = self.original_df[col].nunique()
                if unique_val > 50:
                    insights.append(f"ℹ️ Column '{col}' has {unique_val} unique values")
        
        # Check numeric distribution
        if self.numeric_cols:
            for col in self.numeric_cols[:3]:
                skewness = self.df[col].skew()
                if abs(skewness) > 2:
                    insights.append(f"📊 Column '{col}' is highly skewed (skewness: {skewness:.2f})")
        
        # Dataset size insight
        insights.append(f"📈 Dataset shape: {self.original_df.shape[0]} rows × {self.original_df.shape[1]} columns")
        
        return insights
