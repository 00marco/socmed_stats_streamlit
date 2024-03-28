# Test
streamlit run main.py 

# Deploy
git push

# Update submodule
git submodule update --remote
pip install -r requirements.txt --force-reinstall

# Build docker image
docker build -t socmed_stats_streamlit .
docker run -p 8501:8501 socmed_stats_streamlit
