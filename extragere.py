#MIT License

#Copyright (c) [2026] [Toader Sara]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.




import requests
import pandas as pd
import sys
import csv
import time
import email.utils

GITHUB_TOKEN = "<TOKEN>"

def get_api_status(session):
    """Verifica starea generala a rezervorului de cereri pentru contul curent."""
    try:
        res = session.get("https://api.github.com/rate_limit", timeout=10)
        if res.status_code == 200:
            data = res.json()
            headers = res.headers
            
            server_date_str = headers.get('Date')
            server_date_dt = email.utils.parsedate_to_datetime(server_date_str)
            server_now_timestamp = server_date_dt.timestamp()
            
            reset_timestamp = data['resources']['core']['reset']
            remaining = data['resources']['core']['remaining']
            
            secunde_pana_la_reset = reset_timestamp - server_now_timestamp
            minute_reset = round(secunde_pana_la_reset / 60)
            
            minute_reset = max(0, min(60, minute_reset))
            
            return remaining, 5000, minute_reset
    except Exception as e:
        print(f"Eroare la verificare status: {e}")
    return "N/A", "N/A", "N/A"

def fetch_data_for_multiple_repos(repo_configs):
    all_final_data = []
    total_repo = len(repo_configs)
    
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    for i, (repo_path, state_filter) in enumerate(repo_configs):
        rem, lim_max, min_reset = get_api_status(session)
        print(f"\n[{i+1}/{total_repo}] Incep extragerea pentru: {repo_path}")
        print(f"Ai {rem} cereri disponibile din {lim_max} (Resetare in {min_reset} minute)")
        
        page = 1
        while True:
            url = f"https://api.github.com/repos/{repo_path}/pulls?state={state_filter}&per_page=100&page={page}"
            
            try:
                res = session.get(url, timeout=15)
                
                if res.status_code != 200:
                    print(f"Eroare la {repo_path} (Cod {res.status_code}). Trecem la urmatorul.")
                    break

                prs_list = res.json()
                if not prs_list:
                    break

                print(f"Procesez pagina {page} ({len(prs_list)} PR-uri).")

                for pr in prs_list:
                    pr_num = pr['number']
                    detail_url = f"https://api.github.com/repos/{repo_path}/pulls/{pr_num}"
                    
                    res_detail = session.get(detail_url, timeout=15)
                    
                    
                    ramase_live = int(res_detail.headers.get('X-RateLimit-Remaining', 0))
                    limita = int(res_detail.headers.get('X-RateLimit-Limit', 5000))
                    consumate_total = limita - ramase_live
                    
                    sys.stdout.write(f"\rProcesez PR #{pr_num} | Cereri consumate: {consumate_total} | Cereri ramase: {ramase_live}   ")
                    sys.stdout.flush()

            
                    if ramase_live < 5:
                        _, _, minute_asteptare = get_api_status(session)
                        secunde_somn = (minute_asteptare * 60) + 10 
                        print(f"\n\nLimita de 5000 atinsa! Scriptul ia o pauza de {minute_asteptare} minute.")
                        print(f"Nu inchide fereastra. Extragerea va continua automat.")
                        time.sleep(secunde_somn)
                        print("\nLimita API a fost resetata. Continuam extragerea.")
            

                    if res_detail.status_code != 200:
                        continue

                    info = res_detail.json()
                    
                
                    created = info['created_at'].replace('T', ' ').replace('Z', '')
                    merged = info['merged_at'].replace('T', ' ').replace('Z', '') if info['merged_at'] else "N/A"
                    
                  
                    linii_totale = info.get('additions', 0) + info.get('deletions', 0)
                    if linii_totale < 50:
                        complexitate = "Mic"
                    elif linii_totale < 250:
                        complexitate = "Mediu"
                    else:
                        complexitate = "Mare"

                    all_final_data.append({
                        "Index": len(all_final_data) + 1,
                        "PR_ID": pr_num,
                        "Stadiu": info['state'],
                        "Complexitate": complexitate,
                        "Repo": repo_path, 
                        "Titlu": info['title'],
                        "Autor": info['user']['login'],
                        "Data Deschidere": created,
                        "Data Inchidere": merged,
                        "Comentarii": info.get('comments', 0) + info.get('review_comments', 0),
                        "Linii schimbate": linii_totale
                    })
                
                print("") 
                page += 1

            except Exception as e:
                print(f"\nEroare tehnica! Problema la {repo_path}: {e}")
                break

    if all_final_data:
        df = pd.DataFrame(all_final_data)
        nume_fisier = "Raport_GitHub.csv"
        df.to_csv(nume_fisier, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"\nSucces! Raportul contine {len(all_final_data)} PR-uri salvate.")
        print(f"Fisier generat: {nume_fisier}")
    else:
        print("\nNu s-au gasit date de salvat.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUtilizare: python extragere.py repo1:stare repo2:stare ...")
    else:
        argumente = sys.argv[1:]
        configuratii = []
        
        for arg in argumente:
            if ":" in arg:
                nume_repo, stare_repo = arg.split(":")
                configuratii.append((nume_repo, stare_repo))
            else:
               
                configuratii.append((arg, "all"))
        
        fetch_data_for_multiple_repos(configuratii)