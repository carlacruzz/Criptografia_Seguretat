# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:40:32 2026

@author: laura
"""

def gmul(a,b): #mixcolumns
    # Multiplicació en el camp finit GF(2^8) amb el polinomi 0x11B
    p = 0
    for i in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a <<= 1
        if hi:
            a ^= 0x1b
        b >>= 1
    return p % 256

def print_matrix_hex(titol, state):
    """Imprimeix la matriu d'estat 4x4 en format hexadecimal (ex: 0a, f3)"""
    print(f"\n--- {titol} ---")
    for r in range(4):
        # Format {val:02x} assegura que sempre tingui 2 dígits (ex: 0f en lloc de f)
        fila_hex = [f"{state[r][c]:02x}" for c in range(4)]
        print("[" + ", ".join(fila_hex) + "]")

def generate_sbox():
    """Genera la taula S-Box dinàmicament calculant l'invers en GF(2^8) i la transformació afí"""
    sbox = [0] * 256
    for i in range(256):
        # 1. Trobar l'invers multiplicatiu
        inv = 0
        if i != 0:
            for j in range(1, 256):
                if gmul(i, j) == 1:
                    inv = j
                    break
        
        # 2. Transformació afí
        s = inv
        xformed = s ^ (s << 1) ^ (s << 2) ^ (s << 3) ^ (s << 4)
        xformed = (xformed ^ (xformed >> 8)) & 0xFF
        sbox[i] = xformed ^ 0x63
        
    return sbox

def generate_rcon():
    """Genera les constants de ronda (RCON)"""
    rcon = [0] * 11
    rcon[1] = 0x01
    for i in range(2, 11):
        rcon[i] = gmul(rcon[i-1], 0x02)
    return rcon

# Generem les taules globalment en iniciar
SBOX = generate_sbox()
RCON = generate_rcon()



# FUNCIONS D'ESTAT I MATRIUS
def bytes_to_matrix(b):
    """Converteix 16 bytes en una matriu 4x4 (omplint per columnes)"""
    return [[b[4*c + r] for c in range(4)] for r in range(4)]

def matrix_to_bytes(matrix): # no necessària
    """Converteix la matriu 4x4 d'estat de nou a una tira de 16 bytes"""
    return bytes(matrix[r][c] for c in range(4) for r in range(4))



# EXPANSIÓ DE CLAU
def key_expansion(key_bytes):
    """Expandeix la clau de 16 bytes en 11 subclaus (round keys) de 4x4 matrius"""
    w = [[key_bytes[4*i + j] for j in range(4)] for i in range(4)]
    
    for i in range(4, 44):
        temp = w[i-1][:]
        if i % 4 == 0:
            # RotWord
            temp = temp[1:] + temp[:1]
            # SubWord
            temp = [SBOX[b] for b in temp]
            # XOR amb RCON al primer byte
            temp[0] ^= RCON[i // 4]
            
        w.append([w[i-4][j] ^ temp[j] for j in range(4)])
    
    # Agrupem les "words" en matrius 4x4 per cada ronda
    round_keys = []
    for i in range(0, 44, 4):
        # Transposem perquè 'w' són columnes, i add_round_key espera r,c
        mat = [[w[i+c][r] for c in range(4)] for r in range(4)]
        round_keys.append(mat)
        
    return round_keys



# RONDES I TRANSFORMACIONS
def add_round_key(state, key):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= key[i][j]

def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = SBOX[state[i][j]]

def shift_rows(state):
    state[1] = state[1][1:] + state[1][:1]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][3:] + state[3][:3]
    
def mix_columns(state):
    temp_state = [[0 for _ in range(4)] for _ in range(4)]
    for c in range(4):
        temp_state[0][c] = gmul(0x02, state[0][c]) ^ gmul(0x03, state[1][c]) ^ state[2][c] ^ state[3][c]
        temp_state[1][c] = state[0][c] ^ gmul(0x02, state[1][c]) ^ gmul(0x03, state[2][c]) ^ state[3][c]
        temp_state[2][c] = state[0][c] ^ state[1][c] ^ gmul(0x02, state[2][c]) ^ gmul(0x03, state[3][c])
        temp_state[3][c] = gmul(0x03, state[0][c]) ^ state[1][c] ^ state[2][c] ^ gmul(0x02, state[3][c])
    
    for r in range(4):
        for c in range(4):
            state[r][c] = temp_state[r][c]

def aes_encrypt(message_bytes, key_bytes):
    state = bytes_to_matrix(message_bytes)
    round_keys = key_expansion(key_bytes)
    
    # --- ADDROUNDKEY (La primera crida és a la Ronda 0) ---
    print_matrix_hex("AddRoundKey (Entrada)", state)
    add_round_key(state, round_keys[0])
    print_matrix_hex("AddRoundKey (Sortida)", state)
    
    # Rondes 1 a 9
    for round_num in range(1, 10):
        if round_num == 1:
            # --- SUBBYTES (Primera crida) ---
            print_matrix_hex("SubBytes (Entrada)", state)
            sub_bytes(state)
            print_matrix_hex("SubBytes (Sortida)", state)
            
            # --- SHIFTROWS (Primera crida) ---
            print_matrix_hex("ShiftRows (Entrada)", state)
            shift_rows(state)
            print_matrix_hex("ShiftRows (Sortida)", state)
            
            # --- MIXCOLUMNS (Primera crida) ---
            print_matrix_hex("MixColumns (Entrada)", state)
            mix_columns(state)
            print_matrix_hex("MixColumns (Sortida)", state)
            
            # L'AddRoundKey de la ronda 1 no la imprimim perquè ja hem imprès la inicial
            add_round_key(state, round_keys[round_num])
        else:
            # Execució normal per a les rondes 2 a 9 (sense imprimir)
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, round_keys[round_num])
            
    # Ronda 10 (Final)
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_keys[10])
    
    print("\n")
    
    return matrix_to_bytes(state)
    


if __name__ == "__main__":

    m = "LAURA-CARLA-AES!"
    k = "CLAU-SECRETA-123"
    
    # convertim a bytes
    m_bytes = m.encode('utf-8')
    k_bytes = k.encode('utf-8')
    
    print(f"Text: {m}")
    print(f"Clau utilitzada: {k}")
    
    ciphertext = aes_encrypt(m_bytes, k_bytes)
    
    print("\nText xifrat (en format Hexadecimal):")
    print(ciphertext.hex())

    # activitat 2
    from Crypto.Cipher import AES
    cipher = AES.new(k_bytes, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    print("\nText desxifrat:", plaintext.decode())