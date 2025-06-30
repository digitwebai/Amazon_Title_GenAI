import streamlit as st
import pandas as pd
import openai
from typing import List, Dict
from jinja2 import Template
import os
from dotenv import load_dotenv
import io
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Amazon Title Generator",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pricing for gpt-4o-mini (June 2024)
INPUT_COST_PER_1M = 0.06   # USD/1M
OUTPUT_COST_PER_1M = 2.40  # USD/1M

def initialize_openai():
    """Initialize OpenAI client with API key"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return False
    
    openai.api_key = api_key
    
    # Test API connection with timeout
    try:
        with st.spinner("Testing OpenAI connection..."):
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, can you respond?"}
                ],
                timeout=10  # 10 second timeout
            )
        st.success("✅ OpenAI connection successful!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to connect to OpenAI API: {str(e)}")
        st.info("💡 Make sure your API key is correct and you have sufficient credits.")
        return False

def create_prompt(old_title: str, description: str, examples: List[Dict] = None) -> str:
    """Create a few-shot prompt with examples using Jinja2 template"""
    
    template_string = """Generate Amazon product titles from descriptions. Follow these examples:

    {# Built-in few-shot examples #}
    {% set builtin_examples = [
      {
        'Bullet Points': 'Wireless Bluetooth headphones with active noise cancellation, 30-hour battery life, premium leather ear cushions, compatible with iPhone and Android devices, includes carrying case',
        'Title': 'Wireless Bluetooth Headphones with Active Noise Cancelling, 30H Battery Life, Premium Leather Cushions - Compatible iPhone Android with Carrying Case'
      },
      {
        'Bullet Points': 'Stainless steel water bottle, double wall vacuum insulated, keeps drinks cold 24 hours hot 12 hours, leak-proof design, 32 oz capacity, BPA free, available in multiple colors',
        'Title': 'Stainless Steel Water Bottle 32oz - Double Wall Vacuum Insulated, Keeps Cold 24H Hot 12H, Leak-Proof BPA Free'
      },
      {
        'Bullet Points': 'Gaming mechanical keyboard with RGB backlighting, blue switches, anti-ghosting technology, aluminum frame, detachable USB-C cable, compatible with PC Mac',
        'Title': 'Gaming Mechanical Keyboard RGB Backlit Blue Switches - Anti-Ghosting Aluminum Frame, Detachable USB-C Cable PC Mac Compatible'
      },
      {
        'Bullet Points': 'Yoga mat non-slip surface, eco-friendly TPE material, 6mm thick extra cushioning, lightweight portable design, includes carrying strap, 72 inch length',
        'Title': 'Yoga Mat Non-Slip 6mm Thick Extra Cushion - Eco-Friendly TPE Material 72" Lightweight Portable with Carrying Strap'
      },
      {
        'Bullet Points': 'Smart fitness tracker with heart rate monitor, sleep tracking, waterproof IP68 rating, 7-day battery life, step counter, smartphone notifications',
        'Title': 'Smart Fitness Tracker Heart Rate Monitor Sleep Tracking - Waterproof IP68, 7-Day Battery, Step Counter Smartphone Notifications'
      }
    ] %}

    {% for example in builtin_examples %}
    Example {{ loop.index }}:
    Description: {{ example['Bullet Points'] }}
    Title: {{ example['Title'] }}

    {% endfor %}

    {# Additional custom examples if provided #}
    {% if examples %}
    {% for example in examples[:5] %}
    Example {{ loop.index + builtin_examples|length }}:
    Description: {{ example['Bullet Points'] }}
    Title: {{ example['Title'] }}

    {% endfor %}
    {% endif %}

    Guidelines:
    - Keep titles under 200 characters, with critical keywords in the first 80 characters.
    - Include keywords from the {{ old_title }} that are missing in the description (MUST include within the first 80 characters if missing from the description).
    - Avoid brand names like Ledsone.
    - Must include the shape and pack details if available.
    - Avoid using synonyms (e.g., 'retro' and 'vintage' are synonyms).
    - The first 80 characters should provide a clear description of the product; avoid compatibility information.
    - Generate Amazon specific title considering above instructions.

    Now generate a title for:
    Description: {{ description }}
    Title:"""

    template = Template(template_string)
    prompt = template.render(
        old_title=old_title or '',
        description=description or '',
        examples=examples or []
    )
    return prompt

def generate_title(old_title: str, description: str, temperature: float = 1) -> tuple:
    """Generate a single title for a given product description"""
    try:
        prompt = create_prompt(old_title, description, None)
        
        with st.spinner("Generating title..."):
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating compelling Amazon product titles that drive sales and improve search visibility."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                timeout=30  # 30 second timeout
            )

        title = response.choices[0].message.content.strip()
        
        # Calculate cost
        input_tokens = response['usage']['total_tokens'] - response['usage']['completion_tokens']
        output_tokens = response['usage']['completion_tokens']
        
        cost = (
            (input_tokens / 1000000) * INPUT_COST_PER_1M +
            (output_tokens / 1000000) * OUTPUT_COST_PER_1M
        )
        
        return title, cost, input_tokens, output_tokens
        
    except Exception as e:
        st.error(f"❌ Error generating title: {str(e)}")
        return None, None, None, None

def process_batch_data_with_examples(examples_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
    """Process batch data using examples from competitors file and test data"""
    results = []
    total_cost = 0
    
    # Convert examples DataFrame to list of dictionaries for few-shot learning
    examples_list = []
    if not examples_df.empty:
        examples_list = examples_df[['Title', 'Bullet Points']].to_dict(orient='records')
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in test_df.iterrows():
        status_text.text(f"Processing row {idx + 1} of {len(test_df)}...")
        
        # Handle different column names for test data
        old_title = ''
        description = ''
        
        if 'Title ' in row:  # Note the space after 'Title'
            old_title = str(row['Title ']) if pd.notna(row['Title ']) else ''
        elif 'Title' in row:
            old_title = str(row['Title']) if pd.notna(row['Title']) else ''
        elif 'title' in row:
            old_title = str(row['title']) if pd.notna(row['title']) else ''
            
        if 'Bullet Points' in row:
            description = str(row['Bullet Points']) if pd.notna(row['Bullet Points']) else ''
        elif 'bullet_points' in row:
            description = str(row['bullet_points']) if pd.notna(row['bullet_points']) else ''
        elif 'Description' in row:
            description = str(row['Description']) if pd.notna(row['Description']) else ''
        
        if not description or description.strip() == '':
            st.warning(f"Row {idx + 1}: No description found")
            continue
            
        # Generate title with examples
        title, cost, input_tokens, output_tokens = generate_title_with_examples(
            old_title, description, examples_list
        )
        
        if title:
            results.append({
                'old_title': old_title,
                'bullet_points': description,
                'new_title': title,
                'cost': cost,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            })
            total_cost += cost
        else:
            st.error(f"Row {idx + 1}: Failed to generate title")
        
        progress_bar.progress((idx + 1) / len(test_df))
        time.sleep(0.1)  # Small delay to prevent rate limiting
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results), total_cost

def generate_title_with_examples(old_title: str, description: str, examples: List[Dict], temperature: float = 1) -> tuple:
    """Generate a single title using custom examples from competitors file"""
    try:
        prompt = create_prompt(old_title, description, examples)
        
        with st.spinner("Generating title with examples..."):
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating compelling Amazon product titles that drive sales and improve search visibility."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                timeout=30
            )

        title = response.choices[0].message.content.strip()
        
        # Calculate cost
        input_tokens = response['usage']['total_tokens'] - response['usage']['completion_tokens']
        output_tokens = response['usage']['completion_tokens']
        
        cost = (
            (input_tokens / 1000000) * INPUT_COST_PER_1M +
            (output_tokens / 1000000) * OUTPUT_COST_PER_1M
        )
        
        return title, cost, input_tokens, output_tokens
        
    except Exception as e:
        st.error(f"❌ Error generating title: {str(e)}")
        return None, None, None, None

def process_batch_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process batch data and generate titles (original method)"""
    results = []
    total_cost = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        status_text.text(f"Processing row {idx + 1} of {len(df)}...")
        
        # Handle different column names
        old_title = ''
        description = ''
        
        if 'Title' in row:
            old_title = str(row['Title']) if pd.notna(row['Title']) else ''
        elif 'title' in row:
            old_title = str(row['title']) if pd.notna(row['title']) else ''
            
        if 'Bullet Points' in row:
            description = str(row['Bullet Points']) if pd.notna(row['Bullet Points']) else ''
        elif 'bullet_points' in row:
            description = str(row['bullet_points']) if pd.notna(row['bullet_points']) else ''
        elif 'Description' in row:
            description = str(row['Description']) if pd.notna(row['Description']) else ''
        
        if not description or description.strip() == '':
            st.warning(f"Row {idx + 1}: No description found")
            continue
            
        title, cost, input_tokens, output_tokens = generate_title(old_title, description)
        
        if title:
            results.append({
                'old_title': old_title,
                'bullet_points': description,
                'new_title': title,
                'cost': cost,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            })
            total_cost += cost
        else:
            st.error(f"Row {idx + 1}: Failed to generate title")
        
        progress_bar.progress((idx + 1) / len(df))
        time.sleep(0.1)  # Small delay to prevent rate limiting
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results), total_cost

def main():
    st.title("🛒 Amazon Title Generator")
    st.markdown("Generate compelling Amazon product titles using Few-Shot Learning with GPT-4")
    
    # Sidebar
    st.sidebar.header("Settings")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 1.0, 0.1, 
                                   help="Controls randomness in title generation")
    
    # Check OpenAI connection
    if st.sidebar.button("Test OpenAI Connection"):
        initialize_openai()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["Single Title", "Batch Processing", "Advanced Batch (2 Files)", "About"])
    
    with tab1:
        st.header("Generate Single Title")
        
        col1, col2 = st.columns(2)
        
        with col1:
            old_title = st.text_area("Original Title (Optional)", 
                                   placeholder="Enter the original product title...",
                                   height=100)
            
        with col2:
            description = st.text_area("Product Description", 
                                     placeholder="Enter product description or bullet points...",
                                     height=100)
        
        if st.button("Generate Title", type="primary"):
            if not description:
                st.error("Please enter a product description")
            else:
                # Check OpenAI connection first
                if not initialize_openai():
                    st.stop()
                
                title, cost, input_tokens, output_tokens = generate_title(
                    old_title, description, temperature
                )
                
                if title:
                    st.success("✅ Title generated successfully!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Generated Title")
                        st.write(f"**{title}**")
                        
                        if old_title:
                            st.subheader("Original Title")
                            st.write(old_title)
                    
                    with col2:
                        st.subheader("Cost Analysis")
                        st.metric("Total Cost", f"${cost:.6f}")
                        st.metric("Input Tokens", input_tokens)
                        st.metric("Output Tokens", output_tokens)
                        
                        st.subheader("Title Statistics")
                        st.metric("Title Length", len(title))
                        st.metric("First 80 chars", len(title[:80]))
    
    with tab2:
        st.header("Batch Processing (Single File)")
        
        uploaded_file = st.file_uploader(
            "Upload Excel file with 'Title' and 'Bullet Points' columns",
            type=['xlsx', 'xls']
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ File uploaded successfully! Found {len(df)} rows")
                
                # Display preview
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Show column names for debugging
                st.subheader("Column Names")
                st.write(f"Available columns: {list(df.columns)}")
                
                if st.button("Process All Titles", type="primary"):
                    # Check OpenAI connection first
                    if not initialize_openai():
                        st.stop()
                    
                    results_df, total_cost = process_batch_data(df)
                    
                    if not results_df.empty:
                        st.success(f"✅ Processed {len(results_df)} titles successfully!")
                        
                        # Display results
                        st.subheader("Generated Titles")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Cost summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Cost", f"${total_cost:.6f}")
                        with col2:
                            st.metric("Average Cost per Title", f"${total_cost/len(results_df):.6f}")
                        with col3:
                            st.metric("Titles Generated", len(results_df))
                        
                        # Download button
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            results_df.to_excel(writer, index=False, sheet_name='Generated Titles')
                        output.seek(0)
                        
                        st.download_button(
                            label="Download Results",
                            data=output.getvalue(),
                            file_name="amazon_titles_generated.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("No titles were generated successfully")
                        
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("💡 Make sure your Excel file has the correct format with 'Title' and 'Bullet Points' columns.")
    
    with tab3:
        st.header("Advanced Batch Processing (Two Files)")
        st.markdown("""
        **Upload two Excel files:**
        1. **Competitors File**: Contains examples with 'Title' and 'Bullet Points' columns (like Amazon_Competitors.xlsx)
        2. **Test File**: Contains data to process with 'Title ' (with space) and 'Bullet Points' columns (like Amazon_Data.xlsx)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Competitors File (Examples)")
            competitors_file = st.file_uploader(
                "Upload competitors/examples Excel file",
                type=['xlsx', 'xls'],
                key="competitors"
            )
            
            if competitors_file is not None:
                try:
                    competitors_df = pd.read_excel(competitors_file, sheet_name=0)
                    st.success(f"✅ Competitors file uploaded! Found {len(competitors_df)} examples")
                    
                    # Display preview
                    st.subheader("Competitors Preview")
                    st.dataframe(competitors_df.head(), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error reading competitors file: {str(e)}")
        
        with col2:
            st.subheader("Test File (Data to Process)")
            test_file = st.file_uploader(
                "Upload test data Excel file",
                type=['xlsx', 'xls'],
                key="test"
            )
            
            if test_file is not None:
                try:
                    test_df = pd.read_excel(test_file, sheet_name=0)  # Sheet 2 like original script
                    st.success(f"✅ Test file uploaded! Found {len(test_df)} rows to process")
                    
                    # Display preview
                    st.subheader("Test Data Preview")
                    st.dataframe(test_df.head(), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error reading test file: {str(e)}")
        
        # Process button
        if competitors_file is not None and test_file is not None:
            if st.button("Process with Examples", type="primary", key="process_advanced"):
                # Check OpenAI connection first
                if not initialize_openai():
                    st.stop()
                
                try:
                    # Read files again to ensure they're available
                    competitors_df = pd.read_excel(competitors_file, sheet_name=0)
                    test_df = pd.read_excel(test_file, sheet_name=0)
                    
                    st.info("🔄 Processing with examples from competitors file...")
                    
                    results_df, total_cost = process_batch_data_with_examples(competitors_df, test_df)
                    
                    if not results_df.empty:
                        st.success(f"✅ Processed {len(results_df)} titles successfully!")
                        
                        # Display results
                        st.subheader("Generated Titles")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Cost summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Cost", f"${total_cost:.6f}")
                        with col2:
                            st.metric("Average Cost per Title", f"${total_cost/len(results_df):.6f}")
                        with col3:
                            st.metric("Titles Generated", len(results_df))
                        
                        # Download button
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            results_df.to_excel(writer, index=False, sheet_name='Generated Titles')
                        output.seek(0)
                        
                        st.download_button(
                            label="Download Results (results.xlsx)",
                            data=output.getvalue(),
                            file_name="results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("No titles were generated successfully")
                        
                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")
    
    with tab4:
        st.header("About")
        st.markdown("""
        ### Amazon Title Generator
        
        This application uses Few-Shot Learning (FSL) with GPT-4 to generate compelling Amazon product titles.
        
        **Features:**
        - Single title generation with cost tracking
        - Batch processing for multiple products
        - Advanced batch processing with two files (like original script)
        - Optimized for Amazon SEO requirements
        - Cost-effective using GPT-4o-mini
        
        **Advanced Batch Processing:**
        - **Competitors File**: Contains example titles and descriptions for few-shot learning
        - **Test File**: Contains data to process (sheet 2, like original script)
        - Uses examples from competitors file to improve title generation quality
        
        **Guidelines:**
        - Titles under 200 characters
        - Critical keywords in first 80 characters
        - Amazon-specific optimization
        - Avoid brand name conflicts
        
        **Technology:**
        - OpenAI GPT-4o-mini
        - Few-Shot Learning
        - Jinja2 templating
        - Streamlit web interface
        
        **Troubleshooting:**
        - If you get connection errors, check your OpenAI API key
        - Ensure you have sufficient API credits
        - Try the "Test OpenAI Connection" button in the sidebar
        """)

if __name__ == "__main__":
    main() 