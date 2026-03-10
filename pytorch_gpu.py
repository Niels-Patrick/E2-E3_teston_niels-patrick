# pour CUDA 12.1

# 1. Mettre à jour les Drivers
# 2. Installer le CUDA Toolkit 12.1

# 3. download bin, lib and include from
# https://developer.nvidia.com/rdp/cudnn-archive

# 4. copy paste in
# C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1

# 5. Check PATH is added
# C:\Program Files\NVIDIA GPU Computing Toolkit

# pip install torch torchvision torchaudio --index-url
# https://download.pytorch.org/whl/cu121

import torch


# --- DÉFINITION DU PÉRIPHÉRIQUE (GPU) ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"PyTorch utilisera le périphérique : {DEVICE}")
# ----------------------------------------


def afficher_infos_gpu_pytorch():
    print("--- 🧠 DIAGNOSTIC PYTORCH GPU ---")

    # 1. Vérification générale
    cuda_disponible = torch.cuda.is_available()
    print(f"CUDA (GPU) disponible : {'✅ OUI' if cuda_disponible else '❌ NON'}")

    if not cuda_disponible:
        print("Arrêt du diagnostic : CUDA non détecté. Veuillez vérifier les pilotes.")  # noqa
        return

    # 2. Nombre de GPU
    nombre_gpu = torch.cuda.device_count()
    print(f"Nombre de GPU détectés : {nombre_gpu}")
    print("-" * 35)

    # 3. Informations détaillées pour chaque GPU
    for i in range(nombre_gpu):
        # Sélection du GPU par son index
        torch.cuda.set_device(i)

        # Récupération des propriétés
        proprietes = torch.cuda.get_device_properties(i)

        print(f"### GPU {i}: ###")
        print(f"  Nom de la carte : {proprietes.name}")

        # Mémoire
        memoire_totale_gb = proprietes.total_memory / (1024**3)
        memoire_allouee_mb = torch.cuda.memory_allocated(i) / (1024**2)
        memoire_en_cache_mb = torch.cuda.memory_reserved(i) / (1024**2)

        print(f"  Mémoire Totale : {memoire_totale_gb:.2f} Go")
        print(f"  Mémoire Actuellement Allouée : {memoire_allouee_mb:.2f} Mo")
        print(f"  Mémoire Mise en Cache : {memoire_en_cache_mb:.2f} Mo")

        # Capacité de calcul (important pour la compatibilité)
        print(f"  Capacité de Calcul (sm) : {proprietes.major}.{proprietes.minor}")  # noqa

        print("-" * 35)


# --- EXÉCUTION DANS LE VENV ---
if __name__ == "__main__":
    afficher_infos_gpu_pytorch()