@app.route('/payment-success')
def payment_success():
    # Aapka purana code jo payment verify karta hai
    plan_key = request.args.get('plan', '1_month')
    
    # Plan ke mutabiq main aur bonus links set kar rahe hain (jo pehle se aapke paas hain)
    # Yeh aapke purane dashboard ko disturb nahi karega, balki wahan data pass karega
    session['active_plan'] = plan_key
    session['payment_success'] = True
    
    # Seedha aapke banaye huye dashboard par redirect kar do
    return redirect(url_for('dashboard'))