import streamlit as st
import pandas as pd
import io
from datetime import datetime

def process_excel_files(ledsone_file, competitor_file):
    """
    Process the uploaded Excel files and create analysis
    """
    try:
        # Read the Excel files
        ledsone_df = pd.read_excel(ledsone_file)
        competitor_df = pd.read_excel(competitor_file)
        
        # Basic info about the datasets
        analysis_results = {
            'ledsone_summary': {
                'total_products': len(ledsone_df),
                'columns': list(ledsone_df.columns),
                'sample_data': ledsone_df.head()
            },
            'competitor_summary': {
                'total_products': len(competitor_df),
                'columns': list(competitor_df.columns),
                'sample_data': competitor_df.head()
            }
        }
        
        return ledsone_df, competitor_df, analysis_results
        
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return None, None, None

def create_output_excel(ledsone_df, competitor_df, analysis_results):
    """
    Create a comprehensive Excel output with multiple sheets
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write original data
        ledsone_df.to_excel(writer, sheet_name='Ledsone_Products', index=False)
        competitor_df.to_excel(writer, sheet_name='Competitor_Products', index=False)
        
        # Create summary sheet
        summary_data = {
            'Metric': [
                'Ledsone Products Count',
                'Competitor Products Count',
                'Ledsone Columns',
                'Competitor Columns',
                'Analysis Date'
            ],
            'Value': [
                analysis_results['ledsone_summary']['total_products'],
                analysis_results['competitor_summary']['total_products'],
                ', '.join(analysis_results['ledsone_summary']['columns']),
                ', '.join(analysis_results['competitor_summary']['columns']),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Analysis_Summary', index=False)
        
        # If both datasets have common columns, create a comparison sheet
        common_columns = set(ledsone_df.columns).intersection(set(competitor_df.columns))
        if common_columns:
            comparison_data = {
                'Dataset': ['Ledsone', 'Competitor'],
                'Record_Count': [len(ledsone_df), len(competitor_df)]
            }
            
            for col in common_columns:
                if col in ledsone_df.columns and col in competitor_df.columns:
                    # Add basic statistics for numeric columns
                    if pd.api.types.is_numeric_dtype(ledsone_df[col]):
                        comparison_data[f'{col}_Ledsone_Avg'] = [ledsone_df[col].mean(), None]
                        comparison_data[f'{col}_Competitor_Avg'] = [None, competitor_df[col].mean()]
            
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df.to_excel(writer, sheet_name='Quick_Comparison', index=False)
    
    output.seek(0)
    return output

def main():
    st.set_page_config(
        page_title="Product Analysis Tool",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Product Analysis Tool")
    st.markdown("Upload your Ledsone and Competitor product Excel files for analysis")
    
    # Create two columns for file uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Ledsone Products")
        ledsone_file = st.file_uploader(
            "Upload Ledsone products Excel file",
            type=['xlsx', 'xls'],
            key="ledsone"
        )
        
    with col2:
        st.subheader("🏭 Competitor Products")
        competitor_file = st.file_uploader(
            "Upload Competitor products Excel file",
            type=['xlsx', 'xls'],
            key="competitor"
        )
    
    # Process files when both are uploaded
    if ledsone_file is not None and competitor_file is not None:
        st.success("Both files uploaded successfully!")
        
        with st.spinner("Processing files..."):
            ledsone_df, competitor_df, analysis_results = process_excel_files(ledsone_file, competitor_file)
        
        if ledsone_df is not None and competitor_df is not None:
            # Display file information
            st.subheader("📋 File Information")
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.write("**Ledsone Products:**")
                st.write(f"- Records: {analysis_results['ledsone_summary']['total_products']}")
                st.write(f"- Columns: {len(analysis_results['ledsone_summary']['columns'])}")
                
                with st.expander("View Ledsone Columns"):
                    st.write(analysis_results['ledsone_summary']['columns'])
                
                with st.expander("Preview Ledsone Data"):
                    st.dataframe(analysis_results['ledsone_summary']['sample_data'])
            
            with info_col2:
                st.write("**Competitor Products:**")
                st.write(f"- Records: {analysis_results['competitor_summary']['total_products']}")
                st.write(f"- Columns: {len(analysis_results['competitor_summary']['columns'])}")
                
                with st.expander("View Competitor Columns"):
                    st.write(analysis_results['competitor_summary']['columns'])
                
                with st.expander("Preview Competitor Data"):
                    st.dataframe(analysis_results['competitor_summary']['sample_data'])
            
            # Generate output file
            st.subheader("⬇️ Download Analysis")
            
            if st.button("Generate Analysis Report", type="primary"):
                with st.spinner("Creating Excel report..."):
                    output_file = create_output_excel(ledsone_df, competitor_df, analysis_results)
                
                # Create download button
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"product_analysis_{timestamp}.xlsx"
                
                st.download_button(
                    label="📥 Download Analysis Report",
                    data=output_file.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.success("Analysis report generated successfully!")
                
                # Show what's included in the report
                st.info("""
                **Report Contents:**
                - **Ledsone_Products**: Original Ledsone data
                - **Competitor_Products**: Original competitor data  
                - **Analysis_Summary**: Key metrics and information
                - **Quick_Comparison**: Basic comparison (if common columns exist)
                """)
    
    else:
        st.info("Please upload both Excel files to proceed with the analysis.")
        
        # Show sample format
        with st.expander("ℹ️ Expected File Format"):
            st.write("""
            **File Requirements:**
            - Excel format (.xlsx or .xls)
            - First row should contain column headers
            - Data should start from the second row
            
            **Common columns for better analysis:**
            - Product Name/ID
            - Price
            - Category
            - Specifications
            - Any other relevant product attributes
            """)

if __name__ == "__main__":
    main()