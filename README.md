## Quick Start

```bash
# Clone and set up the RAG lab
cd rag-app
pip install -r requirements.txt
python app.py

# Run the adversarial eval harness against your RAG
cd eval-harness
pip install -r requirements.txt
python harness.py --target http://localhost:8000 --output reports/run-$(date +%Y%m%d).json
```
