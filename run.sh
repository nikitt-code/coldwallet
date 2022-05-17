echo "Updating ColdWallet"
chmod +x run.sh
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python wallet.py