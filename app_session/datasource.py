import requests
import json
from record import MDXChartDifficulty

class SourceConstant:
    def __init__(self,url='https://otoge-db.net/maimai/data/music-ex-intl.json'):
        try:
            resp = requests.get(url)
            resp.raise_for_status()           # → raises if HTTP status is 4xx/5xx
            self.data = resp.json()                # → parses JSON into dict/list
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve data: {e}")
            self.data = None
    
    def get(self) -> dict:
        if not self.data: return {}
        res = {}
        for e in self.data:
            song = e["title"]
            res[song] = {'constants':{'STD':{},'DX':{}}}
            if 'dx_lev_mas' in e:
                mas_i,exp_i, adv_i, bas_i = 0.0,0.0,0.0,0.0
                if "dx_lev_mas_i" in e and e["dx_lev_mas_i"] == "": mas_i = 0.0
                elif "dx_lev_mas_i" in e: mas_i = e["dx_lev_mas_i"]
                if "dx_lev_exp_i" in e and e["dx_lev_exp_i"] == "": exp_i = 0.0
                elif "dx_lev_exp_i" in e: exp_i = e["dx_lev_exp_i"]
                if "dx_lev_adv_i" in e and e["dx_lev_adv_i"] == "": adv_i = 0.0
                elif "dx_lev_adv_i" in e: adv_i = e["dx_lev_adv_i"]
                if "dx_lev_bas_i" in e and e["dx_lev_bas_i"] == "": bas_i = 0.0
                elif "dx_lev_bas_i" in e: bas_i = e["dx_lev_bas_i"]

                if "dx_lev_remas_i" in e and e["dx_lev_remas_i"] != '':
                    res[song]['constants']['DX']['ReMASTER'] = float(e["dx_lev_remas_i"])
                res[song]['constants']['DX']['MASTER'] = float(mas_i)
                res[song]['constants']['DX']['EXPERT'] = float(exp_i)
                res[song]['constants']['DX']['ADVANCED'] = float(adv_i)
                res[song]['constants']['DX']['BASIC'] = float(bas_i)
            elif 'lev_mas' in e:
                mas_i,exp_i, adv_i, bas_i = 0.0,0.0,0.0,0.0
                if "lev_mas_i" in e and e["lev_mas_i"] == "": mas_i = 0.0
                elif "lev_mas_i" in e: mas_i = e["lev_mas_i"]
                if "lev_exp_i" in e and e["lev_exp_i"] == "": exp_i = 0.0
                elif "lev_exp_i" in e: exp_i = e["lev_exp_i"]
                if "lev_adv_i" in e and e["lev_adv_i"] == "": adv_i = 0.0
                elif "lev_adv_i" in e: adv_i = e["lev_adv_i"]
                if "lev_bas_i" in e and e["lev_bas_i"] == "": bas_i = 0.0
                elif "lev_bas_i" in e: bas_i = e["lev_bas_i"]

                if "lev_remas_i" in e and e["lev_remas_i"] != '':
                    res[song]['constants']['STD']['ReMASTER'] = float(e["lev_remas_i"])
                res[song]['constants']['STD']['MASTER'] = float(mas_i)
                res[song]['constants']['STD']['EXPERT'] = float(exp_i)
                res[song]['constants']['STD']['ADVANCED'] = float(adv_i)
                res[song]['constants']['STD']['BASIC'] = float(bas_i)
        return res
            
            
            
            