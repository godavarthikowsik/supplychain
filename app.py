from flask import Flask, render_template, request
from web3 import Web3

app = Flask(__name__)

ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
web3.eth.default_account = web3.eth.accounts[0]

contract_address = "0x8e4da55c9fC4dB41659524e79E82159D62De757d"
contract_abi = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "productId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "to",
          "type": "address"
        }
      ],
      "name": "OwnershipTransferred",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "productId",
          "type": "uint256"
        }
      ],
      "name": "ProductDelivered",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "productId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "manufacturer",
          "type": "string"
        }
      ],
      "name": "ProductRegistered",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_manufacturer",
          "type": "string"
        }
      ],
      "name": "registerProduct",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_productId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_newOwner",
          "type": "address"
        }
      ],
      "name": "transferOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_productId",
          "type": "uint256"
        }
      ],
      "name": "markAsDelivered",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_productId",
          "type": "uint256"
        }
      ],
      "name": "getProduct",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "manufacturer",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "currentOwner",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "isDelivered",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_productId",
          "type": "uint256"
        }
      ],
      "name": "getOwnershipHistory",
      "outputs": [
        {
          "internalType": "address[]",
          "name": "",
          "type": "address[]"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)


@app.route('/')
def index():
    return render_template('connect.html')

@app.route('/welcome')
def welcome():
  return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_product():
    if request.method == 'POST':
        name = request.form['name']
        manufacturer = request.form['manufacturer']
        try:
            tx_hash = contract.functions.registerProduct(name, manufacturer).transact({
                'from': web3.eth.default_account
            })
            web3.eth.wait_for_transaction_receipt(tx_hash)
            return f"Product '{name}' registered successfully with manufacturer '{manufacturer}'."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('register.html')


@app.route('/transfer', methods=['GET', 'POST'])
def transfer_ownership():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        new_owner = request.form['new_owner']
        try:
            tx_hash = contract.functions.transferOwnership(product_id, new_owner).transact({
                'from': web3.eth.default_account
            })
            web3.eth.wait_for_transaction_receipt(tx_hash)
            return f"Ownership of product ID {product_id} transferred to '{new_owner}'."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('transfer.html')


@app.route('/deliver', methods=['GET', 'POST'])
def mark_as_delivered():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        try:
            tx_hash = contract.functions.markAsDelivered(product_id).transact({
                'from': web3.eth.default_account
            })
            web3.eth.wait_for_transaction_receipt(tx_hash)
            return f"Product ID {product_id} marked as delivered."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('deliver.html')


@app.route('/product', methods=['GET', 'POST'])
def get_product_details():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        try:
            product_details = contract.functions.getProduct(product_id).call()
            return f"Product Details: {product_details}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('product.html')


@app.route('/history', methods=['GET', 'POST'])
def get_ownership_history():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        try:
            history = contract.functions.getOwnershipHistory(product_id).call()
            return f"Ownership History: {history}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('history.html')


if __name__ == '__main__':
    app.run(debug=True)
