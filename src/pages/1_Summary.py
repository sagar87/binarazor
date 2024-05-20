from pathlib import Path
import sys
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from database import get_samples


data = get_samples("CD8")
st.header("Something")
st.write(data)