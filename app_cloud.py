import streamlit as st
import pandas as pd
import openai
from typing import List, Dict
from jinja2 import Template
import os
import io
import time
import tempfile

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
    """Initialize OpenAI client with API key - Streamlit Cloud optimized"""
    # Try to get API key from different sources
    api_key = os.getenv('OPENAI_API_KEY')
    
    # If not found in environment, try Streamlit secrets
    if not api_key:
        try:
            api_key = st.secrets.get("openai", {}).get("api_key")
        except:
            pass
    
    if not api_key:
        st.error("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable in Streamlit Cloud.")
        st.info("💡 Go to your app settings in Streamlit Cloud and add the OPENAI_API_KEY environment variable.")
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
                'Original Title': old_title,
                'Description': description,
                'Generated Title': title,
                'Cost (USD)': cost,
                'Input Tokens': input_tokens,
                'Output Tokens': output_tokens
            })
            total_cost += cost
        
        # Update progress
        progress_bar.progress((idx + 1) / len(test_df))
    
    progress_bar.empty()
    status_text.empty()
    
    if results:
        st.success(f"✅ Generated {len(results)} titles successfully!")
        st.info(f"💰 Total cost: ${total_cost:.4f}")
    
    return pd.DataFrame(results)

def generate_title_with_examples(old_title: str, description: str, examples: List[Dict], temperature: float = 1) -> tuple:
    """Generate a single title using few-shot examples"""
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
    """Process batch data without examples"""
    results = []
    total_cost = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        status_text.text(f"Processing row {idx + 1} of {len(df)}...")
        
        # Handle different column names
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
            
        # Generate title
        title, cost, input_tokens, output_tokens = generate_title(old_title, description)
        
        if title:
            results.append({
                'Original Title': old_title,
                'Description': description,
                'Generated Title': title,
                'Cost (USD)': cost,
                'Input Tokens': input_tokens,
                'Output Tokens': output_tokens
            })
            total_cost += cost
        
        # Update progress
        progress_bar.progress((idx + 1) / len(df))
    
    progress_bar.empty()
    status_text.empty()
    
    if results:
        st.success(f"✅ Generated {len(results)} titles successfully!")
        st.info(f"💰 Total cost: ${total_cost:.4f}")
    
    return pd.DataFrame(results)

def main():
    """Main Streamlit application"""
    
    # Initialize OpenAI
    if not initialize_openai():
        st.stop()
    
    # Sidebar
    st.sidebar.title("🛒 Amazon Title Generator")
    st.sidebar.markdown("Generate compelling Amazon product titles using AI")
    
    # Main content
    st.title("🛒 Amazon Title Generator")
    st.markdown("Generate SEO-optimized Amazon product titles using GPT-4")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Single Title", "Batch Processing", "About", "Settings"])
    
    with tab1:
        st.header("🎯 Single Title Generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            old_title = st.text_area("Original Title (Optional)", 
                                   placeholder="Enter the original product title...",
                                   height=100)
            
            description = st.text_area("Product Description", 
                                     placeholder="Enter product description, bullet points, or features...",
                                     height=200)
            
            temperature = st.slider("Creativity Level", 0.0, 2.0, 1.0, 0.1,
                                  help="Higher values = more creative, Lower values = more consistent")
        
        with col2:
            if st.button("🚀 Generate Title", type="primary"):
                if description.strip():
                    with st.spinner("Generating title..."):
                        title, cost, input_tokens, output_tokens = generate_title(
                            old_title, description, temperature
                        )
                    
                    if title:
                        st.success("✅ Title Generated Successfully!")
                        
                        # Display results
                        st.subheader("Generated Title:")
                        st.write(f"**{title}**")
                        
                        # Character count
                        char_count = len(title)
                        st.metric("Character Count", char_count)
                        
                        if char_count > 200:
                            st.warning("⚠️ Title exceeds 200 characters (Amazon recommendation)")
                        
                        # Cost analysis
                        st.subheader("💰 Cost Analysis:")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Cost", f"${cost:.4f}")
                        with col_b:
                            st.metric("Input Tokens", input_tokens)
                        with col_c:
                            st.metric("Output Tokens", output_tokens)
                        
                        # Copy button
                        st.code(title, language=None)
                        
                else:
                    st.error("❌ Please enter a product description")
    
    with tab2:
        st.header("📊 Batch Processing")
        
        # File upload section
        st.subheader("📁 Upload Files")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Competitors File (Optional)**")
            competitors_file = st.file_uploader(
                "Upload Excel file with examples",
                type=['xlsx', 'xls'],
                help="File should contain 'Title' and 'Bullet Points' columns"
            )
        
        with col2:
            st.markdown("**Test Data File**")
            test_file = st.file_uploader(
                "Upload Excel file to process",
                type=['xlsx', 'xls'],
                help="File should contain 'Title' (optional) and 'Bullet Points' columns"
            )
        
        # Process files
        if test_file is not None:
            try:
                test_df = pd.read_excel(test_file)
                st.success(f"✅ Test file loaded: {len(test_df)} rows")
                
                # Show sample data
                with st.expander("📋 Sample Data"):
                    st.dataframe(test_df.head())
                
                # Process options
                st.subheader("⚙️ Processing Options")
                
                use_examples = st.checkbox("Use examples from competitors file", 
                                         value=competitors_file is not None,
                                         help="Use few-shot learning with competitor examples")
                
                if st.button("🚀 Process All Titles", type="primary"):
                    if use_examples and competitors_file is not None:
                        try:
                            examples_df = pd.read_excel(competitors_file)
                            st.success(f"✅ Competitors file loaded: {len(examples_df)} examples")
                            
                            results_df = process_batch_data_with_examples(examples_df, test_df)
                        except Exception as e:
                            st.error(f"❌ Error loading competitors file: {e}")
                            results_df = process_batch_data(test_df)
                    else:
                        results_df = process_batch_data(test_df)
                    
                    if not results_df.empty:
                        st.subheader("📊 Results")
                        st.dataframe(results_df)
                        
                        # Download results
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            results_df.to_excel(writer, index=False, sheet_name='Generated Titles')
                        
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 Download Results (Excel)",
                            data=output.getvalue(),
                            file_name="amazon_titles_generated.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
                st.info("💡 Make sure your Excel file has the correct format:")
                st.markdown("""
                1. **Competitors File**: Contains examples with 'Title' and 'Bullet Points' columns (like Amazon_Competitors.xlsx)
                2. **Test File**: Contains data to process with 'Title ' (with space) and 'Bullet Points' columns (like Amazon_Data.xlsx)
                """)
    
    with tab3:
        st.header("ℹ️ About")
        
        st.markdown("""
        ### 🎯 What is this app?
        This Amazon Title Generator uses **Few-Shot Learning (FSL)** with GPT-4 to create compelling, 
        SEO-optimized product titles that follow Amazon's guidelines.
        
        ### 🚀 Key Features
        - **Single Title Generation**: Generate titles for individual products
        - **Batch Processing**: Process multiple products from Excel files
        - **Cost Tracking**: Monitor API usage and costs
        - **Amazon SEO Optimized**: Follows Amazon's title guidelines
        
        ### 📊 Amazon Title Guidelines
        - **Length**: Under 200 characters
        - **Keywords**: Critical keywords in first 80 characters
        - **Branding**: Avoid brand name conflicts
        - **Specificity**: Include shape and pack details
        - **Uniqueness**: Avoid synonym repetition
        
        ### 💰 Cost Information
        Using GPT-4o-mini for cost efficiency:
        - **Input**: $0.06 per 1M tokens
        - **Output**: $2.40 per 1M tokens
        
        ### 🔧 Technology Stack
        - **AI Model**: OpenAI GPT-4o-mini
        - **Learning Method**: Few-Shot Learning (FSL)
        - **Web Framework**: Streamlit
        - **Template Engine**: Jinja2
        - **Data Processing**: Pandas
        """)
    
    with tab4:
        st.header("⚙️ Settings & Information")
        
        # API Status
        st.subheader("🔌 API Status")
        if initialize_openai():
            st.success("✅ OpenAI API Connected")
        else:
            st.error("❌ OpenAI API Not Connected")
        
        # Cost Information
        st.subheader("💰 Cost Information")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input Cost", f"${INPUT_COST_PER_1M}/1M tokens")
        with col2:
            st.metric("Output Cost", f"${OUTPUT_COST_PER_1M}/1M tokens")
        
        # App Information
        st.subheader("📱 App Information")
        st.info("""
        **Version**: 1.0.0
        **Framework**: Streamlit
        **Model**: GPT-4o-mini
        **Deployment**: Streamlit Cloud
        """)

if __name__ == "__main__":
    main() 