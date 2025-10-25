from flask import Flask, render_template, request, jsonify, send_file
import qrcode
import os
from blockchain.blockchain import Blockchain

app = Flask(__name__)

# Initialize blockchain with difficulty 4
blockchain = Blockchain(difficulty=4)

# Try to load existing blockchain
if not blockchain.load_from_file('blockchain_data.json'):
    print("No existing blockchain found. Starting fresh.")

# Save blockchain after each operation
def save_blockchain():
    blockchain.save_to_file('blockchain_data.json')

# Ensure QR codes directory exists
QR_DIR = 'static/qr_codes'
os.makedirs(QR_DIR, exist_ok=True)


@app.route('/')
def index():
    """Home page with blockchain statistics"""
    products = blockchain.get_all_products()
    stats = blockchain.get_blockchain_stats()
    is_valid, message = blockchain.is_chain_valid()
    
    return render_template('index.html', 
                         products=products,
                         stats=stats,
                         chain_valid=is_valid,
                         validation_message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Product registration page"""
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        manufacturer = request.form.get('manufacturer')
        batch_number = request.form.get('batch_number')
        manufacture_date = request.form.get('manufacture_date')
        
        # Register manufacturer if new
        manufacturer_info = blockchain.register_manufacturer(manufacturer)
        
        # Create transaction with signature
        product_id = blockchain.create_transaction(
            product_name=product_name,
            manufacturer=manufacturer,
            batch_number=batch_number,
            manufacture_date=manufacture_date,
            private_key=manufacturer_info['private_key']
        )
        
        # Mine the block (add to blockchain)
        block = blockchain.mine_pending_transactions()
        
        # SAVE BLOCKCHAIN TO FILE
        blockchain.save_to_file('blockchain_data.json')
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        verification_url = f"http://localhost:5000/verify?id={product_id}"
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(QR_DIR, f"{product_id}.png")
        img.save(qr_path)
        
        return render_template('register.html',
                             success=True,
                             product_id=product_id,
                             block_index=block.index if block else None,
                             block_hash=block.hash if block else None,
                             qr_code_path=f"qr_codes/{product_id}.png")
    
    return render_template('register.html', success=False)


@app.route('/verify')
def verify():
    """Product verification page"""
    product_id = request.args.get('id', '')
    
    if product_id:
        product_data = blockchain.verify_product(product_id)
        
        if product_data:
            return render_template('product_details.html',
                                 product=product_data,
                                 authenticated=True)
        else:
            return render_template('product_details.html',
                                 authenticated=False,
                                 message="Product not found in blockchain")
    
    return render_template('verify.html')


@app.route('/explorer')
def explorer():
    """Blockchain explorer - view all blocks"""
    blocks = []
    for i in range(len(blockchain.chain)):
        block_data = blockchain.get_block_by_index(i)
        blocks.append(block_data)
    
    stats = blockchain.get_blockchain_stats()
    is_valid, message = blockchain.is_chain_valid()
    
    return render_template('explorer.html',
                         blocks=blocks,
                         stats=stats,
                         chain_valid=is_valid,
                         validation_message=message)


@app.route('/block/<int:index>')
def block_details(index):
    """View detailed block information"""
    block_data = blockchain.get_block_by_index(index)
    
    if block_data:
        return render_template('block_details.html',
                             block=block_data,
                             total_blocks=len(blockchain.chain))
    else:
        return "Block not found", 404


@app.route('/manufacturers')
def manufacturers():
    """View registered manufacturers"""
    return render_template('manufacturers.html',
                         manufacturers=blockchain.manufacturers)


@app.route('/api/verify/<product_id>')
def api_verify(product_id):
    """API endpoint for product verification"""
    product_data = blockchain.verify_product(product_id)
    
    if product_data:
        return jsonify({
            'success': True,
            'product': product_data
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Product not found'
        }), 404


@app.route('/api/blockchain')
def get_blockchain():
    """API endpoint to get entire blockchain"""
    chain_data = [block.to_dict() for block in blockchain.chain]
    stats = blockchain.get_blockchain_stats()
    
    return jsonify({
        'chain': chain_data,
        'stats': stats
    })


@app.route('/api/block/<int:index>')
def get_block(index):
    """API endpoint to get specific block"""
    block_data = blockchain.get_block_by_index(index)
    
    if block_data:
        return jsonify(block_data)
    else:
        return jsonify({'error': 'Block not found'}), 404


@app.route('/api/stats')
def get_stats():
    """API endpoint for blockchain statistics"""
    return jsonify(blockchain.get_blockchain_stats())


@app.route('/download_qr/<product_id>')
def download_qr(product_id):
    """Download QR code"""
    qr_path = os.path.join(QR_DIR, f"{product_id}.png")
    if os.path.exists(qr_path):
        return send_file(qr_path, as_attachment=True)
    return "QR Code not found", 404


if __name__ == '__main__':
    print("=" * 60)
    print("🔗 BLOCKCHAIN-BASED PRODUCT AUTHENTICITY SYSTEM")
    print("=" * 60)
    print("Features enabled:")
    print("  ✓ Product data stored INSIDE blocks")
    print("  ✓ Merkle Tree for transaction verification")
    print("  ✓ Digital Signatures for manufacturers")
    print("  ✓ Proof of Work (difficulty: 4)")
    print("  ✓ Transaction-based architecture")
    print("  ✓ Block Explorer")
    print("  ✓ Complete chain validation")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("Press CTRL+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)