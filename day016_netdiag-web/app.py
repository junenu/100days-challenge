import re
import socket
import subprocess
import platform
import ipaddress
import time
from flask import Flask, render_template, request, jsonify
import requests as http_requests

try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    HAS_NETIFACES = False

app = Flask(__name__)

_SAFE_HOST_RE = re.compile(r'^[a-zA-Z0-9.\-_]+$')


def _safe_host(value: str) -> bool:
    return bool(_SAFE_HOST_RE.match(value)) and len(value) <= 253


def get_network_info() -> dict:
    if HAS_NETIFACES:
        try:
            gateways = netifaces.gateways()
            default_gw = gateways.get('default', {})
            if netifaces.AF_INET in default_gw:
                gateway_ip, interface = default_gw[netifaces.AF_INET]
                iface_addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in iface_addrs:
                    addr = iface_addrs[netifaces.AF_INET][0]
                    ip = addr.get('addr', 'N/A')
                    netmask = addr.get('netmask', 'N/A')
                    try:
                        net = ipaddress.IPv4Network(f'{ip}/{netmask}', strict=False)
                        subnet = str(net)
                    except Exception:
                        subnet = 'N/A'
                    return {
                        'ip': ip,
                        'netmask': netmask,
                        'subnet': subnet,
                        'gateway': gateway_ip,
                        'interface': interface,
                        'status': 'ok',
                    }
        except Exception:
            pass

    # Fallback: UDP trick to discover local IP
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        return {
            'ip': ip,
            'netmask': 'N/A',
            'subnet': 'N/A',
            'gateway': 'N/A',
            'interface': 'N/A',
            'status': 'partial',
        }
    except Exception:
        pass

    return {
        'ip': 'N/A', 'netmask': 'N/A', 'subnet': 'N/A',
        'gateway': 'N/A', 'interface': 'N/A', 'status': 'error',
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/network-info')
def network_info():
    return jsonify(get_network_info())


@app.route('/api/ping', methods=['POST'])
def ping():
    target = (request.json or {}).get('target', '').strip()
    if not target:
        return jsonify({'error': 'ターゲットを入力してください'}), 400
    if not _safe_host(target):
        return jsonify({'error': '無効なアドレスです（英数字・ドット・ハイフンのみ）'}), 400

    count_flag = '-n' if platform.system() == 'Windows' else '-c'
    cmd = ['ping', count_flag, '4', target]
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        elapsed = round(time.time() - start, 2)
        return jsonify({
            'output': result.stdout + result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0,
            'elapsed': elapsed,
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'タイムアウト（15秒）', 'success': False})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/dns', methods=['POST'])
def dns():
    domain = (request.json or {}).get('domain', '').strip()
    if not domain:
        return jsonify({'error': 'ドメインを入力してください'}), 400
    if not _safe_host(domain):
        return jsonify({'error': '無効なドメイン名です'}), 400

    start = time.time()
    try:
        results = socket.getaddrinfo(domain, None)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        seen: set = set()
        addresses = []
        for r in results:
            addr = r[4][0]
            family = 'IPv4' if r[0] == socket.AF_INET else 'IPv6'
            if (addr, family) not in seen:
                seen.add((addr, family))
                addresses.append({'address': addr, 'family': family})
        return jsonify({
            'domain': domain,
            'addresses': addresses,
            'success': True,
            'elapsed_ms': elapsed_ms,
        })
    except socket.gaierror as e:
        return jsonify({'error': f'DNS 解決失敗: {e}', 'success': False})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/http', methods=['POST'])
def http_check():
    url = (request.json or {}).get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL を入力してください'}), 400
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    start = time.time()
    try:
        resp = http_requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={'User-Agent': 'NetworkDiag/1.0'},
        )
        elapsed_ms = round((time.time() - start) * 1000, 2)
        final_url = str(resp.url)
        return jsonify({
            'url': final_url,
            'status_code': resp.status_code,
            'status_text': resp.reason,
            'elapsed_ms': elapsed_ms,
            'content_type': resp.headers.get('Content-Type', ''),
            'server': resp.headers.get('Server', ''),
            'redirected': final_url != url,
            'success': resp.status_code < 400,
        })
    except http_requests.exceptions.Timeout:
        return jsonify({'error': 'タイムアウト（10秒）', 'success': False})
    except http_requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'接続エラー: {e}', 'success': False})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


if __name__ == '__main__':
    print('ネットワーク診断ツール起動中 → http://localhost:5016')
    app.run(host='0.0.0.0', port=5016, debug=False)
