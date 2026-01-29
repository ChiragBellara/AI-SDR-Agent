import json
import time
import asyncio
import streamlit as st
import pandas as pd
from utils.json_utils import validate_sources
from scrapper import CrawlURLs
from pathlib import Path
from logger.universal_logger import setup_logger

LOG_PATH = Path("logs/app.log")
logger = setup_logger('AI_SDR.Runner')
STORAGE_PATH = Path("../storage/identities/")
crawler = CrawlURLs()


st.set_page_config(page_title="AI-SDR Discovery", layout="wide")
st.title("AI-SDR: Company Discovery")
uploaded_file = st.file_uploader(
    "Upload Sources JSON (Company Names) & URLs", type=["json"])
if uploaded_file is not None:
    try:
        raw_data = json.load(uploaded_file)
        is_valid, result = validate_sources(raw_data)

        if is_valid:
            st.success("✅ File format verified! Ready to crawl.")
            df = pd.DataFrame(raw_data)
            st.dataframe(df, width='stretch')
            if st.button("Start Discovery", type="primary"):
                with st.status(f"Crawling {len(raw_data)} companies... this may take a few minutes.", expanded=True) as status:
                    logger.info("Starting Classification")
                    start_time = time.perf_counter()
                    for src in raw_data:
                        company_name, company_url = src['name'], src['url']
                        status.write(
                            f"Crawling {company_name} starting at {company_url}")
                        logger.info(f"Extracting data for {company_name}")
                        site_content = crawler.handler(company_url)
                        status.write(
                            f"Completed extracting data for {company_name}. Writing the data to Lead Card file.")
                        if site_content:
                            crawler.write_to_file(
                                site_content, STORAGE_PATH / f"{company_name}.json")

                    logger.info("Extraction Complete.")
                    logger.info(f"Number of websites crawled: {len(raw_data)}")
                    logger.info(
                        f"Total time taken: {round((time.perf_counter() - start_time) * 1000, 2)}")

                    status.update(label="All Leads Processed!",
                                  state="complete")
        else:
            st.error(f"❌ Validation Error: {result}")
            st.info(
                "Ensure your JSON looks like: `[{'name': 'Stripe', 'url': 'https://stripe.com'}]`")
    except json.JSONDecodeError:
        st.error("❌ The file is not a valid JSON.")
