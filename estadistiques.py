# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:03:03 2026

@author: laura
"""

import os
import matplotlib.pyplot as plt
from scipy.stats import chisquare
from aes import aes_encrypt

def main():
    # 1. Paràmetres de l'experiment
    num_blocks = 100000  
    # clau fixa
    k = "CLAU-SECRETA-123"
    k_bytes = k.encode('utf-8')
    
    # Creem una llista de 256 posicions (inicialitzades a 0) per comptar les aparicions de cada valor de byte (0 a 255)
    byte_counts = [0] * 256
    
    print(f"Iniciant generacio i xifratge de {num_blocks} blocs (1.600.000 bytes)...")
    
    # 2. Bucle principal
    for i in range(num_blocks):
        # Generem un missatge aleatori de 16 bytes per a cada bloc
        m_bytes = os.urandom(16)
        
        # El xifrem amb la implementació d'AES
        c_bytes = aes_encrypt(m_bytes, k_bytes)
        
        # Comptem la freqüència de cada byte en el text xifrat resultant
        for byte_val in c_bytes:
            byte_counts[byte_val] += 1
            
        # Mostrem el progrés
        if (i + 1) % 10000 == 0:
            print(f"  Progres: {i + 1} / {num_blocks} blocs processats...")

    # 3. Anàlisi Estadística
    total_bytes = num_blocks * 16
    # Si la distribució és perfectament uniforme, cada byte hauria d'aparèixer exactament:
    expected_frequency = total_bytes / 256.0
    expected_counts = [expected_frequency] * 256
    
    print(" RESULTATS DE L'ANALISI ESTADISTICA (TEST CHI-QUADRAT)")
    print(f"Total de bytes xifrats: {total_bytes}")
    print(f"Frequencia esperada per byte: {expected_frequency}")
    
    # Fem el test de Chi-quadrat
    chi2_stat, p_value = chisquare(f_obs=byte_counts, f_exp=expected_counts)
    
    print(f"Estadistic Chi-quadrat: {chi2_stat:.4f}")
    print(f"P-valor (p-value):      {p_value:.6f}")
    
    if p_value > 0.05:
        print("\nCONCLUSIO: El p-valor es > 0.05. No es pot rebutjar la hipotesi nul·la.")
        print("La distribucio dels bytes ES compatible amb una distribucio uniforme.")
    else:
        print("\nCONCLUSIO: El p-valor es <= 0.05. Es rebutja la hipotesi nul·la.")
        print("La distribucio NO sembla uniforme.")
    
    # 4. Representació gràfica
    plt.figure(figsize=(12, 6))
    
    # Dibuixem les barres de freqüències observades
    plt.bar(range(256), byte_counts, color='mediumpurple', edgecolor='black', width=1.0, alpha=0.7)
    
    # Dibuixem una línia horitzontal marcant la freqüència esperada (teòrica)
    plt.axhline(y=expected_frequency, color='red', linestyle='dashed', linewidth=2, 
                label=f'Freq. Esperada Uniforme ({expected_frequency})')
    
    plt.title("Distribucio de les Frequencies dels Bytes al Text Xifrat", fontsize=14)
    plt.xlabel("Valor del Byte (0 - 255)", fontsize=12)
    plt.ylabel("Frequencia d'aparicio", fontsize=12)
    plt.xlim(-1, 256)
    
    # Ajustem l'eix Y per centrar-nos on estan les dades
    y_min = min(byte_counts) * 0.95
    y_max = max(byte_counts) * 1.05
    plt.ylim(y_min, y_max)
    
    plt.legend()
    plt.grid(axis='y', alpha=0.5)
    
    # Guardem el gràfic per a l'informe
    nom_arxiu = "grafic_estadistica_bytes.png"
    plt.savefig(nom_arxiu, dpi=300, bbox_inches='tight')
    print(f"S'ha generat i guardat el grafic amb el nom: '{nom_arxiu}'.")
    
    plt.show()

if __name__ == "__main__":
    main()
