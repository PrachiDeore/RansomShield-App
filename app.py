import streamlit as st
import random
import json
import base64
import datetime
import time
import re
from io import BytesIO
import os

# Optional visualization libs (add to requirements if you want Network Map)
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from PIL import Image
    NETWORKX_AVAILABLE = True
except Exception:
    NETWORKX_AVAILABLE = False

# ---------------------------
# RansomShield Enhanced — App with requested features
# Features included:
# - Fake File Encryption Visualizer (upload multiple files, UI-only)
# - Real-Time Kill-Chain Demo (animated timeline)
# - Fake Command-Line Ransomware Output (terminal simulator)
# - ML-style Phishing Detector (rule-based classifier)
# - Ransom Note Generator (customizable, downloadable)
# - Incident Response Chatbot (rule-based guidance)
# - Audit Log Simulator (fake SOC logs)
# - Phishing Inbox Simulator (new)
# - Network Map Infection Demo (new)
# - Attack Lab (videos/gifs) (new)
# - Breach Cost Calculator (new)
#
# Safety: This app NEVER opens, modifies, encrypts, or transmits uploaded files.
# It only uses filenames and in-session UI state to simulate behaviour.
# ---------------------------

# ---------------------------
# Helpers
# ---------------------------

def set_page_config():
    st.set_page_config(page_title="RansomShield Enhanced", page_icon="🛡️", layout="wide")


CSS = '''
section[data-testid="stSidebar"] { background-color: #071029; }
.stApp { background: linear-gradient(180deg,#020617,#04102b); color: #e6eaf3 }
h1, h2, h3 { color: #e6f2ff }
.card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 12px; margin-bottom: 12px }
.ransom-box { background: rgba(128,0,0,0.12); padding: 14px; border-radius: 8px }
.terminal { background: #000; color: #0f0; padding: 12px; border-radius: 6px; font-family: monospace }
.small-muted { color: #94a3b8; font-size: 13px }
'''

def local_css(css: str):
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def init_state():
    if 'files' not in st.session_state:
        st.session_state.files = []
    if 'infected' not in st.session_state:
        st.session_state.infected = False
    if 'ransom_msg' not in st.session_state:
        st.session_state.ransom_msg = ''
    if 'analytics' not in st.session_state:
        st.session_state.analytics = {'simulations_run': 0, 'phishing_clicked': 0, 'quizzes_taken': 0, 'avg_quiz_score': 0}
    if 'chat' not in st.session_state:
        st.session_state.chat = []
    # inbox session data
    if 'inbox_marks' not in st.session_state:
        st.session_state.inbox_marks = {}
    if 'inbox_score' not in st.session_state:
        st.session_state.inbox_score = 0
    if 'inbox_attempts' not in st.session_state:
        st.session_state.inbox_attempts = 0
    if 'open_mail' not in st.session_state:
        st.session_state.open_mail = None

# ---------------------------
# Simulation functions
# ---------------------------

def fake_encrypt_uploaded_files(uploaded_files):
    """Simulate encryption by showing filenames and a fake progress bar per file."""
    # Do NOT read file contents — only use metadata
    results = []
    placeholder = st.empty()
    for f in uploaded_files:
        fname = f.name
        results.append({'orig': fname, 'locked': False, 'display': fname})

    # simulate sequential encryption
    for idx, r in enumerate(results):
        fname = r['orig']
        locked_name = fname + '.locked'
        ph = st.empty()
        ph.markdown(f"**Encrypting:** `{fname}`")
        p = st.progress(0)
        for i in range(0, 101, 5):
            p.progress(i)
            time.sleep(0.03)
        r['locked'] = True
        r['display'] = locked_name
        ph.markdown(f"**{locked_name}** — 🔒 Encrypted (simulated)")
    return results

def generate_ransom_note_for_files(files, family='Generic', amount='0.5 BTC'):
    # Create a ransom note referencing file names (UI-only)
    note = f"*** {family} RANSOM NOTE (SIMULATION) ***\n\n"
    note += "The files listed below have been encrypted:\n"
    for f in files:
        note += f"- {f['display']}\n"
    note += f"\nTo recover your files send {amount} to wallet: 1AaBbCccD... (SIMULATION)\n"
    note += "Timer: 48:00:00"
    return note

# ---------------------------
# Kill-chain animation
# ---------------------------

def show_kill_chain_animation(details=False):
    stages = [
        ('Initial Access', 'Phishing or exploit grants access'),
        ('Execution', 'Payload executes on host'),
        ('Persistence', 'Malicious service / scheduled task created'),
        ('Privilege Escalation', 'Attempt to gain higher privileges'),
        ('Lateral Movement', 'Spreading to other hosts'),
        ('Impact', 'Data encrypted and ransom note dropped')
    ]
    ph = st.empty()
    for name, desc in stages:
        ph.markdown(f"### {name}\n{desc}")
        time.sleep(0.8)
    ph.markdown('### Kill chain demonstration complete (simulation)')
    if details:
        st.markdown('**Notes:** This is a simplified educational sequence mapping to common attack steps.')

# ---------------------------
# Terminal simulator
# ---------------------------

def terminal_simulator(target_files=None):
    if target_files is None:
        target_files = ['project_code.py', 'taxes.xlsx', 'notes.txt']
    st.markdown('## Terminal — Simulated Ransomware Output')
    term = st.empty()
    log_lines = []
    log_lines.append('Starting scan of file system...')
    for f in target_files:
        log_lines.append(f'Found file: {f}')
        time.sleep(0.2)
    log_lines.append('Beginning encryption routine...')
    for f in target_files:
        log_lines.append(f'Encrypting: {f} -> {f}.locked')
        time.sleep(0.25)
    log_lines.append('Encryption complete. Ransom note created: READ_ME_NOW.txt')
    term.code('\n'.join(log_lines), language='')

# ---------------------------
# Phishing detector (rule-based)
# ---------------------------

PHISHING_KEYWORDS = {
    'urgent': 2,
    'verify': 1,
    'password': 2,
    'bank': 1,
    'click': 1,
    'login': 1,
    'update': 1,
    'invoice': 1,
    'salary': 1,
}

def phishing_score(text: str):
    t = text.lower()
    score = 0
    for k, v in PHISHING_KEYWORDS.items():
        if k in t:
            score += v
    # suspicious sender pattern
    if re.search(r'^[^@]+@[^@]+\.(ru|cn|tk|ml)$', t, re.IGNORECASE):
        score += 3
    # many links
    links = len(re.findall(r'http[s]?://', t))
    score += min(links * 2, 6)
    # short message with urgent keywords
    if len(t.split()) < 20 and any(k in t for k in ['urgent','verify','password']):
        score += 2
    # Normalize to 0-100 style
    max_score = 20
    pct = int(min(score / max_score * 100, 100))
    return pct

# ---------------------------
# Incident response chatbot (rule-based)
# ---------------------------

CHAT_FLOW = {
    'opened suspicious file': [
        'Step 1: Disconnect the device from the network immediately.',
        'Step 2: Notify your IT/security team and preserve the device as-is.',
        'Do NOT power off the device if evidence collection is needed; follow IT guidance.'
    ],
    'machine encrypted': [
        'Isolate the machine — disconnect network, unplug ethernet/Wi-Fi.',
        'Preserve logs and contact incident response. Do NOT pay ransom without consulting authority.'
    ],
    'phishing email': [
        'Do not click links or open attachments. Report the email to your security team.',
        'Change passwords if you suspect credential compromise.'
    ]
}

def chatbot_respond(message: str):
    m = message.lower()
    for key in CHAT_FLOW.keys():
        if key in m:
            return '\n'.join(CHAT_FLOW[key])
    # fallback guidance
    return ('If this is urgent: isolate affected systems, notify IT, preserve evidence (screenshots/logs),'
            ' and follow your organization incident response playbook.')

# ---------------------------
# Audit log simulator
# ---------------------------

def generate_audit_logs(count=12):
    levels = ['INFO', 'WARN', 'ERROR', 'CRITICAL']
    actions = [
        'User login success',
        'User login failure',
        'Suspicious PowerShell execution',
        'File write to backup folder',
        'SMB connection from 192.168.1.50',
        'Large file read: finances.xlsx',
        'Process created: suspicious.exe',
        'Network scan detected',
        'Potential data exfiltration',
        'Ransom note dropped: READ_ME_NOW.txt'
    ]
    now = datetime.datetime.now()
    logs = []
    for i in range(count):
        time_stamp = (now - datetime.timedelta(seconds=(count - i) * random.randint(10, 80))).isoformat()
        logs.append(f"[{time_stamp}] {random.choice(levels)} - {random.choice(actions)}")
    return '\n'.join(logs)

# ---------------------------
# New Feature: Phishing Inbox Simulator
# ---------------------------

SAMPLE_INBOX = [
    {
        'id': 1, 'from': 'hr@acme-corp.com', 'subject': 'Payroll Update Required',
        'snippet': 'Please download attached payroll_update.zip and confirm', 'body': 'Dear employee,\nPlease download payroll_update.zip and run to update payroll.',
        'is_phish': True
    },
    {
        'id': 2, 'from': 'it-support@acme-corp.com', 'subject': 'Password expiry notice',
        'snippet': 'Your password will expire, log in at https://acme-login.example to renew', 'body': 'Your password will expire. Please login: https://acme-login.example',
        'is_phish': True
    },
    {
        'id': 3, 'from': 'ceo@acme-corp.com', 'subject': 'Team lunch tomorrow',
        'snippet': 'Reminder: Team lunch tomorrow 1PM', 'body': 'Reminder: Team lunch tomorrow 1PM', 'is_phish': False
    },
    {
        'id': 4, 'from': 'vendor@trusted-supplier.com', 'subject': 'Invoice 2025-011',
        'snippet': 'Please find attached invoice_2025.pdf', 'body': 'Please find attached invoice_2025.pdf. Thanks.', 'is_phish': False
    },
    {
        'id': 5, 'from': 'alerts@bank-secure.ru', 'subject': 'Account verification needed',
        'snippet': 'Verify your account immediately', 'body': 'We detected a problem. Verify at http://bank.verify-now.example', 'is_phish': True
    }
]

def page_inbox():
    st.markdown('# Phishing Inbox Simulator')
    st.markdown('Inspect emails from a simulated inbox and mark them as **Phishing** or **Safe**. Your score is tracked in-session.')
    if st.session_state.open_mail is None:
        st.session_state.open_mail = SAMPLE_INBOX[0]['id']

    cols = st.columns([3,1])
    with cols[0]:
        st.markdown('### Inbox')
        for mail in SAMPLE_INBOX:
            st.markdown(f"**From:** `{mail['from']}`  \n**Subject:** {mail['subject']}  \n_{mail['snippet']}_")
            if st.button(f"Open #{mail['id']}", key=f"open_{mail['id']}"):
                st.session_state.open_mail = mail['id']
            st.write('---')

    with cols[1]:
        open_id = st.session_state.get('open_mail', SAMPLE_INBOX[0]['id'])
        mail = next((m for m in SAMPLE_INBOX if m['id'] == open_id), SAMPLE_INBOX[0])
        st.markdown('### Inspector')
        st.markdown(f"**From:** {mail['from']}")
        st.markdown(f"**Subject:** {mail['subject']}")
        st.code(mail['body'])
        mark = st.radio('Mark this email as:', ['Safe', 'Phishing'], index=0, key=f'mark_{mail["id"]}')
        if st.button('Submit Mark', key=f'submit_{mail["id"]}'):
            user_mark = (mark == 'Phishing')
            st.session_state.inbox_attempts += 1
            correct = (user_mark == mail['is_phish'])
            if correct:
                st.session_state.inbox_score += 1
                st.success('Correct')
            else:
                st.error('Incorrect')
            st.session_state.inbox_marks[mail['id']] = user_mark

        st.markdown('### Session Score')
        st.metric('Score', f"{st.session_state.inbox_score}/{max(1, st.session_state.inbox_attempts)}")

    st.write('---')
    st.markdown('**Hints:** Look for suspicious domains, unexpected attachments, urgent language, and mismatched senders.')

# ---------------------------
# New Feature: Network Map (requires networkx + matplotlib)
# ---------------------------

def page_network_map():
    st.markdown('# Network Map — Infection Spread Demo')
    st.markdown('A simple network graph shows how infection can propagate. This is an animation (UI-only).')

    if not NETWORKX_AVAILABLE:
        st.error('Network visualization requires `networkx`, `matplotlib`, and `Pillow`. Install them or remove this page.')
        return

    nodes = st.slider('Number of devices (nodes)', 6, 40, 12)
    infect_seed = st.number_input('Start infection at node (index)', min_value=0, max_value=max(0, nodes-1), value=0, step=1)
    spread_chance = st.slider('Spread probability per edge', 0.0, 1.0, 0.35)
    steps = st.slider('Simulation steps', 3, 12, 6)

    if st.button('Run network simulation'):
        G = nx.erdos_renyi_graph(nodes, 0.2, seed=42)
        pos = nx.spring_layout(G, seed=1)  # stable layout
        infected = set([infect_seed])
        placeholder = st.empty()

        fig = plt.figure(figsize=(6,4))
        for step in range(steps):
            plt.clf()
            colors = ['red' if n in infected else '#66cc66' for n in G.nodes()]
            nx.draw(G, pos, with_labels=True, node_color=colors, node_size=250, edge_color='#999999')
            plt.title(f'Network propagation — Step {step+1}')
            placeholder.pyplot(fig)
            # propagate
            new = set()
            for n in list(infected):
                for nb in G.neighbors(n):
                    if random.random() < spread_chance:
                        new.add(nb)
            infected |= new
            time.sleep(0.7)
        st.success('Simulation complete — infected nodes shown in red.')

# ---------------------------
# New Feature: Attack Lab (media)
# ---------------------------

def page_attack_lab():
    st.markdown('# Attack Lab — Educational Media')
    st.markdown('Collection of short videos and GIFs explaining ransomware steps. Place media files in `assets/` folder or provide YouTube links to embed.')

    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    st.markdown('### Local media (assets/)')
    st.write('If you place files named `killchain.mp4`, `ransom_note.gif`, or `network_scan.mp4` inside `assets/` they will appear below.')

    file_list = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.mp4','.gif','.webm'))]
    if file_list:
        for fname in file_list:
            path = os.path.join(assets_dir, fname)
            st.markdown(f'**{fname}**')
            if fname.lower().endswith('.gif'):
                st.image(path, caption=fname)
            else:
                st.video(path)
            st.write('---')
    else:
        st.info('No local media found in assets/. You can upload or drop files there.')

    st.markdown('### Example external resources')
    st.markdown('- (Optional) Insert YouTube links below to embed educational videos.')
    yt = st.text_input('YouTube URL (embed)', '')
    if yt:
        st.video(yt)

# ---------------------------
# New Feature: Breach Cost Calculator
# ---------------------------

def page_breach_calculator():
    st.markdown('# Breach Cost Calculator — Estimate Impact')
    st.markdown('Enter simple business metrics to estimate the financial impact of a simulated ransomware incident.')

    with st.form('breach_form'):
        employees = st.number_input('Number of employees', min_value=1, value=50)
        avg_salary = st.number_input('Average monthly salary (INR)', min_value=1000, value=40000, step=1000)
        downtime_hours = st.number_input('Estimated downtime (hours)', min_value=1, value=24)
        data_records = st.number_input('Number of sensitive records', min_value=0, value=10000)
        ransom_expected = st.number_input('Expected ransom (INR)', min_value=0, value=2000000, step=10000)
        submit = st.form_submit_button('Estimate')

    if submit:
        # Simple heuristic model
        hourly_wage = avg_salary / 30 / 8
        business_loss = employees * hourly_wage * downtime_hours
        cost_per_record = 20  # INR per record (example)
        data_loss_cost = data_records * cost_per_record
        recovery_costs = business_loss * 0.6 + 0.4 * ransom_expected
        total_estimated = business_loss + data_loss_cost + recovery_costs + ransom_expected

        st.subheader('Estimated Cost Breakdown (INR)')
        st.write(f'- Business interruption: ₹{int(business_loss):,}')
        st.write(f'- Data breach handling: ₹{int(data_loss_cost):,}')
        st.write(f'- Recovery (forensics/restoration): ₹{int(recovery_costs):,}')
        st.write(f'- Ransom (expected): ₹{int(ransom_expected):,}')
        st.markdown(f'**Total estimated impact:** ₹{int(total_estimated):,}')

        summary = f"""Breach Cost Estimate
Date: {datetime.datetime.now().isoformat()}

Employees: {employees}
Avg salary: {avg_salary}
Downtime (hrs): {downtime_hours}
Sensitive records: {data_records}
Ransom expected: {ransom_expected}

Business interruption: {int(business_loss)}
Data breach handling: {int(data_loss_cost)}
Recovery costs: {int(recovery_costs)}
Total estimated: {int(total_estimated)}
"""
        st.download_button('Download estimate (TXT)', data=summary.encode('utf-8'), file_name='breach_estimate.txt')

# ---------------------------
# Pages (existing)
# ---------------------------

def page_home():
    st.markdown('# RansomShield — Enhanced Simulator')
    st.markdown('Safe educational simulator demonstrating ransomware behaviour and defenses.')
    st.write('---')
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown('## Quick actions')
        st.markdown('- Try **Simulator** to upload files and see fake encryption.')
        st.markdown('- Run the **Kill Chain** demo to learn attack steps.')
        st.markdown('- Use the **Phishing Detector** to scan sample emails.')
        st.markdown('- Open **Inbox** to practice phishing identification.')
        st.markdown('- Use **Breach Calculator** to estimate impact.')
    with col2:
        a = st.session_state.analytics
        st.metric('Simulations run', a['simulations_run'])
        st.metric('Phishing checks', a['phishing_clicked'])

def page_simulator():
    st.markdown('# File Upload — Fake Encryption Visualizer')
    st.markdown('Upload files to see a UI-only simulated encryption. **The app never reads or modifies your files.**')
    uploaded = st.file_uploader('Upload one or more files', accept_multiple_files=True)
    if uploaded:
        st.warning('Simulation only — files are not opened. Showing filenames and simulating progress.')
        results = fake_encrypt_uploaded_files(uploaded)
        st.session_state.files = results
        note = generate_ransom_note_for_files(results)
        st.session_state.ransom_msg = note
        st.session_state.analytics['simulations_run'] += 1
        st.markdown('---')
        if st.button('Show ransom note'):
            st.markdown(f"<div class='ransom-box'><pre>{st.session_state.ransom_msg}</pre></div>", unsafe_allow_html=True)

def page_kill_chain():
    st.markdown('# Kill Chain Demonstration')
    st.markdown('Animated, step-by-step overview of a typical ransomware kill chain (educational).')
    if st.button('Run Kill Chain Demo'):
        show_kill_chain_animation(details=True)

def page_terminal():
    st.markdown('# Terminal Simulator (UI-only)')
    st.markdown('A fake command-line output that shows how an attacker might enumerate and encrypt files.')
    targets = [f['orig'] if 'orig' in f else f['name'] for f in st.session_state.files] or ['project_code.py', 'taxes.xlsx', 'notes.txt']
    if st.button('Run terminal simulation'):
        terminal_simulator(targets)

def page_phishing_detector():
    st.markdown('# Phishing Detector (Rule-based Demo)')
    st.markdown('Paste an email (headers+body) or type a sample—this is a local, rule-based demo not a real ML model.')
    text = st.text_area('Email content', height=200)
    if st.button('Scan email'):
        pct = phishing_score(text)
        st.session_state.analytics['phishing_clicked'] += 1
        st.success(f'Phishing likelihood score: {pct}%')
        if pct > 60:
            st.error('High likelihood of phishing — treat with caution')
        elif pct > 30:
            st.warning('Possible phishing indicators found')
        else:
            st.info('Low likelihood by simple heuristics')

def page_ransom_note_generator():
    st.markdown('# Ransom Note Generator (Simulation)')
    st.markdown('Create a custom ransom note for demonstration. This is for educational use only.')
    with st.form('ransom_form'):
        family = st.selectbox('Ransomware family style', ['Generic', 'LockBit', 'REvil', 'WannaCry'])
        amount = st.text_input('Ransom amount', '0.5 BTC')
        victim = st.text_input('Victim / Organization name', 'Acme Corp')
        add_files = st.text_area('Optional: list files (one per line)')
        submitted = st.form_submit_button('Generate note')
    if submitted:
        files = [ln.strip() for ln in add_files.splitlines() if ln.strip()]
        fake_files = [{'display': fn} for fn in files] if files else st.session_state.files or [{'display': 'example.docx'}]
        note = generate_ransom_note_for_files(fake_files, family=family, amount=amount)
        st.markdown('### Preview (simulation)')
        st.markdown(f"<div class='ransom-box'><pre>{note}</pre></div>", unsafe_allow_html=True)
        if st.button('Download ransom note (txt)'):
            b = note.encode('utf-8')
            st.download_button('Download', data=b, file_name='ransom_note_simulation.txt')

def page_chatbot():
    st.markdown('# Incident Response Chatbot (Rule-based)')
    st.markdown('Ask for guidance — the bot provides safe, basic incident response steps.')
    user = st.text_input('Describe the issue', key='chat_input')
    if st.button('Ask') and user:
        resp = chatbot_respond(user)
        st.session_state.chat.append({'q': user, 'a': resp})
    for msg in st.session_state.chat:
        st.markdown(f"**You:** {msg['q']}")
        st.markdown(f"**Bot:** {msg['a']}")

def page_audit_logs():
    st.markdown('# Audit Log Simulator')
    st.markdown('Generate a fake SOC-style log stream to practice detection and SOC workflows.')
    count = st.slider('Log entries', 6, 50, 12)
    if st.button('Generate logs'):
        logs = generate_audit_logs(count)
        st.code(logs)
        if st.button('Download logs as .txt'):
            st.download_button('Download', data=logs.encode('utf-8'), file_name='simulated_audit_logs.txt')

def page_admin():
    st.markdown('# Admin — Session Analytics')
    st.write(json.dumps(st.session_state.analytics, indent=2))
    if st.button('Reset analytics'):
        st.session_state.analytics = {'simulations_run': 0, 'phishing_clicked': 0, 'quizzes_taken': 0, 'avg_quiz_score': 0}
        st.success('Analytics reset')

# ---------------------------
# Main app
# ---------------------------

def main():
    set_page_config()
    local_css(CSS)
    init_state()

    st.sidebar.title('RansomShield Enhanced')
    st.sidebar.markdown('Safe ransomware awareness simulator — enhanced features')
    page = st.sidebar.radio('Navigate', [
        'Home', 'Simulator', 'Kill Chain', 'Terminal', 'Phishing Detector',
        'Inbox', 'Network Map', 'Attack Lab', 'Breach Calculator',
        'Ransom Note', 'Chatbot', 'Audit Logs', 'Admin'
    ])

    if page == 'Home':
        page_home()
    elif page == 'Simulator':
        page_simulator()
    elif page == 'Kill Chain':
        page_kill_chain()
    elif page == 'Terminal':
        page_terminal()
    elif page == 'Phishing Detector':
        page_phishing_detector()
    elif page == 'Inbox':
        page_inbox()
    elif page == 'Network Map':
        page_network_map()
    elif page == 'Attack Lab':
        page_attack_lab()
    elif page == 'Breach Calculator':
        page_breach_calculator()
    elif page == 'Ransom Note':
        page_ransom_note_generator()
    elif page == 'Chatbot':
        page_chatbot()
    elif page == 'Audit Logs':
        page_audit_logs()
    elif page == 'Admin':
        page_admin()

    st.write('---')
    st.markdown('**Safety reminder:** This is a training simulator. It does not modify files or perform any real encryption or network activity.')

if __name__ == '__main__':
    main()
