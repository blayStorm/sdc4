import winreg

def check_windows_proxy_configuration():
    try:
        internet_settings = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
        proxy_enable, _ = winreg.QueryValueEx(internet_settings, 'ProxyEnable')
        if proxy_enable == 1:
            proxy_server, _ = winreg.QueryValueEx(internet_settings, 'ProxyServer')
            winreg.CloseKey(internet_settings)
            return True, proxy_server
        else:
            winreg.CloseKey(internet_settings)
            return False, None
    except FileNotFoundError:
        return False, None