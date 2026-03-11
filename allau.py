# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:27:49 2026

@author: laura
"""

import random
import matplotlib.pyplot as plt
from aes import aes_encrypt

def hamming_distance(bytes1, bytes2):
    """
    Calcula la distància de Hamming (nombre de bits diferents) 
    entre dues seqüències de bytes.
    """
    return sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(bytes1, bytes2))

def flip_random_bit(b_array):
    """
    Inverteix exactament un bit aleatori (posició 0 a 127) 
    d'una seqüència de 16 bytes.
    """
    bit_index = random.randint(0, 127)
    byte_idx = bit_index // 8
    bit_in_byte = bit_index % 8
    
    # Convertim a bytearray perquè ens permeti modificar un byte concret
    new_b = bytearray(b_array)
    # Apliquem una màscara XOR per invertir només el bit desitjat
    new_b[byte_idx] ^= (1 << bit_in_byte)
    
    return bytes(new_b)

def main():
    # 1. Definim el missatge i la clau fixos (els mateixos que a l'Activitat 1)
    m = "LAURA-CARLA-AES!"
    k = "CLAU-SECRETA-123"
    
    m_bytes = m.encode('utf-8')
    k_bytes = k.encode('utf-8')
    
    iterations = 100000
    print(f"Iniciant l'experiment de l'Efecte Allau amb {iterations} iteracions...")
    
    # 2. Xifrem el missatge original (c)
    c_original = aes_encrypt(m_bytes, k_bytes)
    
    distances = []
    
    # 3. Bucle de les 100.000 iteracions
    for i in range(iterations):
        # Genereu m' modificant un bit
        m_prime = flip_random_bit(m_bytes)
        
        # Xifreu m' per obtenir c'
        c_prime = aes_encrypt(m_prime, k_bytes)
        
        # Calculeu la distància de Hamming i guardeu-la
        dist = hamming_distance(c_original, c_prime)
        distances.append(dist)
        
            
    # 4. Anàlisi dels resultats (Mitjana)
    avg_dist = sum(distances) / iterations
    
    print("RESULTATS DE L'EFECTE ALLAU")
    print("Valor teòric esperat: 64.0 bits")
    print(f"Mitjana obtinguda:    {avg_dist:.2f} bits")
    
    # 5. Representació gràfica de la distribució
    plt.figure(figsize=(10, 6))
    
    # Definim els límits de l'eix X per a l'histograma
    bins_range = range(min(distances), max(distances) + 2)
    plt.hist(distances, bins=bins_range, align='left', edgecolor='black', color='cornflowerblue')
    
    # Marquem els valors teòric i real al gràfic
    plt.axvline(x=64, color='red', linestyle='dashed', linewidth=2, label='Teòric (64 bits)')
    plt.axvline(x=avg_dist, color='green', linestyle='dotted', linewidth=2, label=f'Mitjana ({avg_dist:.2f})')
    
    plt.title("Efecte Allau (Avalanche Effect) en AES-128", fontsize=14)
    plt.xlabel("Distància de Hamming (Nombre de bits modificats al text xifrat)", fontsize=12)
    plt.ylabel("Freqüència (Nombre de textos xifrats)", fontsize=12)
    plt.legend()
    plt.grid(axis='y', alpha=0.5)
    
    # Guardem i mostrem la imatge
    nom_arxiu = "grafic_efecte_allau.png"
    plt.savefig(nom_arxiu, dpi=300, bbox_inches='tight')
    print(f"S'ha generat i guardat el gràfic amb el nom: '{nom_arxiu}'.")
    
    plt.show()

if __name__ == "__main__":
    main()