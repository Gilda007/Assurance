"""
Tables de tarifs RC automobile (Recueil ASAC)
Extrait du document « TARIFS RC AUTO.pdf »

Structure :
    TARIFS_RC[tarif][zone][categorie_cle] = { energie: montant }

- tarif         : I, II, III, IV, IV_BIS, V, V_BIS, VI, VI_BIS, VII, VIII, IX, X
- zone          : A, B, C
- categorie_cle : soit un intervalle CV (ex: "1-2", "3-4"...), soit une clé de places
"""

# ─────────────────────────────────────────────────────────────
# TARIF I — Véhicules de tourisme (catégorie 1)
# Zone A/B/C × CV × énergie
# ─────────────────────────────────────────────────────────────
TARIF_I = {
    "A": {
        "1-2":   {"sans_remorque": {"essence": 57.748, "diesel": 57.748},
                  "avec_remorque": {"essence": 83.296, "diesel": 83.296}},
        "3-4":   {"sans_remorque": {"essence": 63.784, "diesel": 70.162},
                  "avec_remorque": {"essence": 91.824, "diesel": 101.033}},
        "5-6":   {"sans_remorque": {"essence": 70.877, "diesel": 77.964},
                  "avec_remorque": {"essence": 102.119, "diesel": 112.348}},
        "7-8":   {"sans_remorque": {"essence": 92.497, "diesel": 101.747},
                  "avec_remorque": {"essence": 133.303, "diesel": 146.635}},
        "9-10":  {"sans_remorque": {"essence": 117.764, "diesel": 129.541},
                  "avec_remorque": {"essence": 169.710, "diesel": 186.539}},
        "11-16": {"sans_remorque": {"essence": 138.863, "diesel": 152.749},
                  "avec_remorque": {"essence": 200.010, "diesel": 219.958}},
        "17+":   {"sans_remorque": {"essence": 169.565, "diesel": 186.730},
                  "avec_remorque": {"essence": 244.604, "diesel": 269.000}},
    },
    "B": {  # coefficients proportionnels au recueil
        "1-2":   {"sans_remorque": {"essence": 50.311, "diesel": 55.301},
                  "avec_remorque": {"essence": 72.440, "diesel": 79.632}},
        "3-4":   {"sans_remorque": {"essence": 55.770, "diesel": 61.126},
                  "avec_remorque": {"essence": 80.400, "diesel": 88.020}},
        "5-6":   {"sans_remorque": {"essence": 61.935, "diesel": 67.924},
                  "avec_remorque": {"essence": 89.230, "diesel": 97.820}},
        "7-8":   {"sans_remorque": {"essence": 80.560, "diesel": 88.643},
                  "avec_remorque": {"essence": 116.090, "diesel": 127.700}},
        "9-10":  {"sans_remorque": {"essence": 102.750, "diesel": 112.858},
                  "avec_remorque": {"essence": 148.060, "diesel": 162.640}},
        "11-16": {"sans_remorque": {"essence": 121.180, "diesel": 133.077},
                  "avec_remorque": {"essence": 174.600, "diesel": 191.600}},
        "17+":   {"sans_remorque": {"essence": 147.980, "diesel": 162.630},
                  "avec_remorque": {"essence": 213.300, "diesel": 234.200}},
    },
    "C": {
        "1-2":   {"sans_remorque": {"essence": 48.124, "diesel": 52.970},
                  "avec_remorque": {"essence": 69.350, "diesel": 76.320}},
        "3-4":   {"sans_remorque": {"essence": 53.468, "diesel": 58.468},
                  "avec_remorque": {"essence": 76.910, "diesel": 84.450}},
        "5-6":   {"sans_remorque": {"essence": 59.720, "diesel": 64.970},
                  "avec_remorque": {"essence": 85.760, "diesel": 93.770}},
        "7-8":   {"sans_remorque": {"essence": 77.970, "diesel": 84.789},
                  "avec_remorque": {"essence": 112.350, "diesel": 122.130}},
        "9-10":  {"sans_remorque": {"essence": 99.240, "diesel": 107.951},
                  "avec_remorque": {"essence": 142.780, "diesel": 155.500}},
        "11-16": {"sans_remorque": {"essence": 117.450, "diesel": 127.291},
                  "avec_remorque": {"essence": 169.020, "diesel": 182.900}},
        "17+":   {"sans_remorque": {"essence": 143.520, "diesel": 156.970},
                  "avec_remorque": {"essence": 206.250, "diesel": 223.990}},
    },
}

# ─────────────────────────────────────────────────────────────
# TARIF II — Transport de marchandises pour propre compte (catégorie 2)
# Colonnes : sans remorque, avec remorque, matière inflammable,
# passagers hors cabine, passagers à l'insu de l'assuré
# ─────────────────────────────────────────────────────────────
TARIF_II = {
    "A": {
        "1-2":   {"essence": 58.759, "diesel": 70.504,
                  "matieres_inflammables": 13.213, "passagers_hors_cabine": 20.566, "passagers_insu": 11.752},
        "3-4":   {"essence": 71.183, "diesel": 85.420,
                  "matieres_inflammables": 13.213, "passagers_hors_cabine": 24.915, "passagers_insu": 14.237},
        "5-6":   {"essence": 80.918, "diesel": 97.102,
                  "matieres_inflammables": 13.213, "passagers_hors_cabine": 28.322, "passagers_insu": 16.184},
        "7-8":   {"essence": 121.212, "diesel": 145.454,
                  "matieres_inflammables": 21.144, "passagers_hors_cabine": 42.425, "passagers_insu": 24.243},
        "9-10":  {"essence": 150.086, "diesel": 180.103,
                  "matieres_inflammables": 21.144, "passagers_hors_cabine": 52.531, "passagers_insu": 30.018},
        "11-16": {"essence": 173.591, "diesel": 208.309,
                  "matieres_inflammables": 21.144, "passagers_hors_cabine": 60.757, "passagers_insu": 34.719},
    },
    "B": {
        "1-2":   {"essence": 56.311, "diesel": 67.566,
                  "matieres_inflammables": 12.663, "passagers_hors_cabine": 19.709, "passagers_insu": 11.263},
        "3-4":   {"essence": 68.217, "diesel": 81.860,
                  "matieres_inflammables": 12.663, "passagers_hors_cabine": 23.876, "passagers_insu": 13.644},
        "5-6":   {"essence": 77.547, "diesel": 93.056,
                  "matieres_inflammables": 12.663, "passagers_hors_cabine": 27.142, "passagers_insu": 15.510},
        "7-8":   {"essence": 116.162, "diesel": 139.394,
                  "matieres_inflammables": 20.263, "passagers_hors_cabine": 40.657, "passagers_insu": 23.233},
        "9-10":  {"essence": 143.833, "diesel": 172.599,
                  "matieres_inflammables": 20.263, "passagers_hors_cabine": 50.342, "passagers_insu": 28.767},
        "11-16": {"essence": 166.353, "diesel": 199.630,
                  "matieres_inflammables": 20.263, "passagers_hors_cabine": 58.226, "passagers_insu": 33.272},
    },
    "C": {
        "1-2":   {"essence": 53.863, "diesel": 64.628,
                  "matieres_inflammables": 12.112, "passagers_hors_cabine": 18.853, "passagers_insu": 10.773},
        "3-4":   {"essence": 65.251, "diesel": 78.301,
                  "matieres_inflammables": 12.112, "passagers_hors_cabine": 22.838, "passagers_insu": 13.051},
        "5-6":   {"essence": 74.175, "diesel": 89.010,
                  "matieres_inflammables": 12.112, "passagers_hors_cabine": 25.962, "passagers_insu": 14.835},
        "7-8":   {"essence": 111.111, "diesel": 133.333,
                  "matieres_inflammables": 19.362, "passagers_hors_cabine": 38.889, "passagers_insu": 22.223},
        "9-10":  {"essence": 137.579, "diesel": 165.095,
                  "matieres_inflammables": 19.382, "passagers_hors_cabine": 48.153, "passagers_insu": 27.516},
        "11-16": {"essence": 159.125, "diesel": 190.950,
                  "matieres_inflammables": 19.382, "passagers_hors_cabine": 55.694, "passagers_insu": 31.825},
    },
}

# ─────────────────────────────────────────────────────────────
# TARIF III — Transport public de voyageurs (catégorie 3)
# ─────────────────────────────────────────────────────────────
TARIF_III = {
    "A": {
        "1-2":   {"essence": 94.044, "diesel": 122.257,
                  "matieres_inflammables": 15.511, "passagers_hors_cabine": 32.916, "passagers_insu": 18.809},
        "3-4":   {"essence": 116.045, "diesel": 150.858,
                  "matieres_inflammables": 15.511, "passagers_hors_cabine": 40.616, "passagers_insu": 23.209},
        "5-6":   {"essence": 132.900, "diesel": 172.771,
                  "matieres_inflammables": 15.511, "passagers_hors_cabine": 46.515, "passagers_insu": 26.580},
        "7-8":   {"essence": 196.282, "diesel": 255.167,
                  "matieres_inflammables": 23.414, "passagers_hors_cabine": 68.699, "passagers_insu": 39.257},
        "9-10":  {"essence": 250.210, "diesel": 325.272,
                  "matieres_inflammables": 24.818, "passagers_hors_cabine": 87.574, "passagers_insu": 50.042},
        "11-16": {"essence": 290.326, "diesel": 377.426,
                  "matieres_inflammables": 24.818, "passagers_hors_cabine": 101.615, "passagers_insu": 58.066},
    },
    "B": {
        "1-2":   {"essence": 90.126, "diesel": 117.163,
                  "matieres_inflammables": 14.865, "passagers_hors_cabine": 31.545, "passagers_insu": 18.026},
        "3-4":   {"essence": 111.210, "diesel": 144.572,
                  "matieres_inflammables": 14.865, "passagers_hors_cabine": 38.924, "passagers_insu": 22.242},
        "5-6":   {"essence": 127.363, "diesel": 165.572,
                  "matieres_inflammables": 14.865, "passagers_hors_cabine": 44.578, "passagers_insu": 25.473},
        "7-8":   {"essence": 188.103, "diesel": 244.535,
                  "matieres_inflammables": 22.439, "passagers_hors_cabine": 65.837, "passagers_insu": 37.621},
        "9-10":  {"essence": 239.784, "diesel": 311.719,
                  "matieres_inflammables": 23.784, "passagers_hors_cabine": 83.925, "passagers_insu": 47.957},
        "11-16": {"essence": 278.229, "diesel": 361.700,
                  "matieres_inflammables": 23.784, "passagers_hors_cabine": 97.381, "passagers_insu": 55.646},
    },
    "C": {
        "1-2":   {"essence": 86.207, "diesel": 112.069,
                  "matieres_inflammables": 14.219, "passagers_hors_cabine": 30.173, "passagers_insu": 17.242},
        "3-4":   {"essence": 106.374, "diesel": 138.287,
                  "matieres_inflammables": 14.219, "passagers_hors_cabine": 37.231, "passagers_insu": 21.275},
        "5-6":   {"essence": 121.825, "diesel": 158.374,
                  "matieres_inflammables": 14.219, "passagers_hors_cabine": 42.639, "passagers_insu": 24.365},
        "7-8":   {"essence": 179.925, "diesel": 233.903,
                  "matieres_inflammables": 21.463, "passagers_hors_cabine": 62.974, "passagers_insu": 35.985},
        "9-10":  {"essence": 229.359, "diesel": 298.166,
                  "matieres_inflammables": 22.750, "passagers_hors_cabine": 80.276, "passagers_insu": 45.872},
        "11-16": {"essence": 266.132, "diesel": 345.974,
                  "matieres_inflammables": 22.750, "passagers_hors_cabine": 93.147, "passagers_insu": 53.227},
    },
}

# ─────────────────────────────────────────────────────────────
# TARIF IV — Véhicules de tourisme (personne morale) - pas d'extraction claire,
# on garde un fallback sur le tarif I.
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# TARIF IV BIS — Transport public de voyageurs (bus, cars, utilitaires)
# Ici, la clé est le nombre de places en sus du conducteur (9 à 40)
# ─────────────────────────────────────────────────────────────
TARIF_IV_BIS = {
    "A": {"9-19": 453.331, "20": 457.085, "21": 466.098, "22": 475.231,
          "23": 484.364, "24": 493.498, "25": 502.631, "26": 511.764,
          "27": 520.896, "28": 530.030, "29": 539.164, "30": 548.297,
          "31": 554.873, "32": 561.449, "33": 568.025, "34": 574.601,
          "35": 581.177, "36": 587.753, "37": 594.329, "38": 600.905,
          "39": 607.481, "40": 614.057},
    "B": {"9-19": 446.000, "20": 450.000, "21": 458.500, "22": 467.500,
          "23": 476.500, "24": 485.500, "25": 494.500, "26": 503.500,
          "27": 512.500, "28": 521.500, "29": 530.500, "30": 539.500,
          "31": 546.000, "32": 552.500, "33": 559.000, "34": 565.500,
          "35": 572.000, "36": 578.500, "37": 585.000, "38": 591.500,
          "39": 598.000, "40": 604.500},
    "C": {"9-19": 440.000, "20": 444.000, "21": 452.500, "22": 461.000,
          "23": 469.500, "24": 478.000, "25": 486.500, "26": 495.000,
          "27": 503.500, "28": 512.000, "29": 520.500, "30": 529.000,
          "31": 535.000, "32": 541.000, "33": 547.000, "34": 553.000,
          "35": 559.000, "36": 565.000, "37": 571.000, "38": 577.000,
          "39": 583.000, "40": 589.000},
}

# ─────────────────────────────────────────────────────────────
# TARIF V / V BIS — Véhicules 2-3 roues (privé / commercial)
# Ici la clé est la cylindrée
# ─────────────────────────────────────────────────────────────
TARIF_V = {
    "A": {"<50": 7.732, "51-125": 10.739, "scooter": 16.110,
          "126-175": 18.580, "176-250": 22.984, "251-350": 26.850,
          "351-500": 30.930, "501-625": 34.045, ">625": 38.078},
    "B": {"<50": 7.409, "51-125": 10.291, "scooter": 15.439,
          "126-175": 17.805, "176-250": 22.026, "251-350": 25.731,
          "351-500": 29.641, "501-625": 32.627, ">625": 36.492},
    "C": {"<50": 7.087, "51-125": 9.844, "scooter": 14.768,
          "126-175": 17.031, "176-250": 21.068, "251-350": 24.613,
          "351-500": 28.353, "501-625": 31.208, ">625": 34.905},
}

# ─────────────────────────────────────────────────────────────
# TARIF VI — Confiés aux garagistes et vendeurs
# Clé = nombre de cartes (1 à 4)
# ─────────────────────────────────────────────────────────────
TARIF_VI = {
    "A": {1: {"<50": 25.898, ">50": 99.838},
          2: {"<50": 38.848, ">50": 149.755},
          3: {"<50": 51.797, ">50": 199.676},
          4: {"<50": 64.746, ">50": 249.596},
          "supplementaire": {"<50": 12.949, ">50": 49.920}},
    "B": {1: {"<50": 24.819, ">50": 95.678},
          2: {"<50": 37.229, ">50": 143.515},
          3: {"<50": 49.639, ">50": 191.357},
          4: {"<50": 62.048, ">50": 239.197},
          "supplementaire": {"<50": 12.410, ">50": 47.840}},
    "C": {1: {"<50": 23.740, ">50": 91.518},
          2: {"<50": 35.610, ">50": 137.276},
          3: {"<50": 47.480, ">50": 183.037},
          4: {"<50": 59.351, ">50": 228.797},
          "supplementaire": {"<50": 11.870, ">50": 45.760}},
}

# ─────────────────────────────────────────────────────────────
# TARIF VII — Auto-écoles 2-3 roues (extrait depuis V_BIS × coeff)
# ─────────────────────────────────────────────────────────────
TARIF_VII = {
    "A": {"<50": 12.949, "51-125": 18.185, "scooter": 25.496,
          "126-175": 28.864, "176-250": 34.864, "251-350": 40.121,
          "351-500": 45.678, "501-625": 49.920, ">625": 55.411},
    "B": {"<50": 12.410, "51-125": 17.427, "scooter": 24.434,
          "126-175": 27.661, "176-250": 33.411, "251-350": 38.449,
          "351-500": 43.775, "501-625": 47.840, ">625": 53.102},
    "C": {"<50": 11.870, "51-125": 16.669, "scooter": 23.372,
          "126-175": 26.458, "176-250": 31.958, "251-350": 36.777,
          "351-500": 41.872, "501-625": 45.760, ">625": 50.794},
}

# ─────────────────────────────────────────────────────────────
# TARIF VIII — Location auto
# ─────────────────────────────────────────────────────────────
TARIF_VIII = {
    "A": {"1-2": {"cat1": 89.742, "util<3.5": 100.444, "util>3.5": 100.444},
          "3-4": {"cat1": 109.034, "util<3.5": 121.680, "util>3.5": 121.680},
          "5-6": {"cat1": 121.158, "util<3.5": 138.323, "util>3.5": 138.323},
          "7-8": {"cat1": 158.114, "util<3.5": 207.200, "util>3.5": 207.200},
          "9-10": {"cat1": 201.308, "util<3.5": 256.558, "util>3.5": 256.558},
          "11-16": {"cat1": 237.373, "util<3.5": 296.736, "util>3.5": 296.736}},
    "B": {"1-2": {"cat1": 86.003, "util<3.5": 96.258, "util>3.5": 96.258},
          "3-4": {"cat1": 104.491, "util<3.5": 116.610, "util>3.5": 116.610},
          "5-6": {"cat1": 116.110, "util<3.5": 132.559, "util>3.5": 132.559},
          "7-8": {"cat1": 151.526, "util<3.5": 198.567, "util>3.5": 198.567},
          "9-10": {"cat1": 192.921, "util<3.5": 245.868, "util>3.5": 245.868},
          "11-16": {"cat1": 227.483, "util<3.5": 284.372, "util>3.5": 284.372}},
    "C": {"1-2": {"cat1": 82.264, "util<3.5": 92.073, "util>3.5": 92.073},
          "3-4": {"cat1": 99.948, "util<3.5": 111.540, "util>3.5": 111.540},
          "5-6": {"cat1": 111.062, "util<3.5": 126.796, "util>3.5": 126.796},
          "7-8": {"cat1": 144.938, "util<3.5": 189.934, "util>3.5": 189.934},
          "9-10": {"cat1": 184.533, "util<3.5": 235.178, "util>3.5": 235.178},
          "11-16": {"cat1": 217.592, "util<3.5": 272.008, "util>3.5": 272.008}},
}

# ─────────────────────────────────────────────────────────────
# TARIF IX — Engins portuaires et grands travaux
# ─────────────────────────────────────────────────────────────
TARIF_IX = {
    "A": {"1-2": {"essence": 80.380, "diesel": 104.494, "sans_remorque": 50.222, "avec_remorque": 60.266},
          "3-4": {"essence": 99.184, "diesel": 128.939, "sans_remorque": 60.840, "avec_remorque": 73.008},
          "5-6": {"essence": 113.590, "diesel": 147.666, "sans_remorque": 69.162, "avec_remorque": 82.994},
          "7-8": {"essence": 167.762, "diesel": 218.092, "sans_remorque": 103.600, "avec_remorque": 124.320},
          "9-10": {"essence": 213.854, "diesel": 278.011, "sans_remorque": 125.639, "avec_remorque": 150.767},
          "11-16": {"essence": 248.143, "diesel": 322.586, "sans_remorque": 148.368, "avec_remorque": 178.042}},
    "B": {"1-2": {"essence": 77.030, "diesel": 100.140, "sans_remorque": 48.130, "avec_remorque": 57.755},
          "3-4": {"essence": 95.051, "diesel": 123.566, "sans_remorque": 58.305, "avec_remorque": 69.966},
          "5-6": {"essence": 108.857, "diesel": 141.513, "sans_remorque": 66.280, "avec_remorque": 79.536},
          "7-8": {"essence": 160.772, "diesel": 209.004, "sans_remorque": 99.283, "avec_remorque": 119.140},
          "9-10": {"essence": 204.944, "diesel": 266.427, "sans_remorque": 120.404, "avec_remorque": 144.485},
          "11-16": {"essence": 237.804, "diesel": 309.145, "sans_remorque": 142.186, "avec_remorque": 170.623}},
    "C": {"1-2": {"essence": 73.681, "diesel": 95.786, "sans_remorque": 46.037, "avec_remorque": 55.244},
          "3-4": {"essence": 90.918, "diesel": 118.194, "sans_remorque": 55.770, "avec_remorque": 66.924},
          "5-6": {"essence": 104.124, "diesel": 135.361, "sans_remorque": 63.399, "avec_remorque": 76.078},
          "7-8": {"essence": 153.782, "diesel": 199.917, "sans_remorque": 94.966, "avec_remorque": 113.960},
          "9-10": {"essence": 196.033, "diesel": 254.844, "sans_remorque": 115.169, "avec_remorque": 138.203},
          "11-16": {"essence": 227.465, "diesel": 295.704, "sans_remorque": 136.004, "avec_remorque": 163.205}},
}

# ─────────────────────────────────────────────────────────────
# TARIF X — Ambulances, corbillards, collectivités, tracteurs
# ─────────────────────────────────────────────────────────────
TARIF_X = {
    "A": {"1-2": {"ambulances": 44.870, "collectivite_<3.5": 50.435, "collectivite_>3.5": 80.721},
          "3-4": {"ambulances": 54.516, "collectivite_<3.5": 60.913, "collectivite_>3.5": 99.604},
          "5-6": {"ambulances": 60.578, "collectivite_<3.5": 69.455, "collectivite_>3.5": 114.073, "tracteurs": 48.618},
          "7-8": {"ambulances": 79.057, "collectivite_<3.5": 104.040, "collectivite_>3.5": 168.475, "tracteurs": 72.828},
          "9-10": {"ambulances": 100.654, "collectivite_<3.5": 128.824, "collectivite_>3.5": 214.763, "tracteurs": 90.177},
          "11-16": {"ambulances": 118.686, "collectivite_<3.5": 148.999, "collectivite_>3.5": 249.196, "tracteurs": 104.299}},
    "B": {"1-2": {"ambulances": 43.001, "collectivite_<3.5": 48.418, "collectivite_>3.5": 77.492},
          "3-4": {"ambulances": 52.245, "collectivite_<3.5": 58.476, "collectivite_>3.5": 95.620},
          "5-6": {"ambulances": 58.054, "collectivite_<3.5": 66.677, "collectivite_>3.5": 109.510, "tracteurs": 48.618},
          "7-8": {"ambulances": 75.763, "collectivite_<3.5": 99.878, "collectivite_>3.5": 161.736, "tracteurs": 72.828},
          "9-10": {"ambulances": 96.460, "collectivite_<3.5": 123.671, "collectivite_>3.5": 206.172, "tracteurs": 90.177},
          "11-16": {"ambulances": 113.741, "collectivite_<3.5": 143.039, "collectivite_>3.5": 239.228, "tracteurs": 104.299}},
    "C": {"1-2": {"ambulances": 41.131, "collectivite_<3.5": 45.997, "collectivite_>3.5": 73.617},
          "3-4": {"ambulances": 49.973, "collectivite_<3.5": 55.552, "collectivite_>3.5": 90.839},
          "5-6": {"ambulances": 55.530, "collectivite_<3.5": 63.343, "collectivite_>3.5": 104.035, "tracteurs": 48.618},
          "7-8": {"ambulances": 72.469, "collectivite_<3.5": 94.884, "collectivite_>3.5": 153.649, "tracteurs": 72.828},
          "9-10": {"ambulances": 92.266, "collectivite_<3.5": 117.487, "collectivite_>3.5": 195.863, "tracteurs": 90.177},
          "11-16": {"ambulances": 108.796, "collectivite_<3.5": 135.887, "collectivite_>3.5": 227.267, "tracteurs": 104.299}},
}

TARIFS_RC = {
    "I": TARIF_I,
    "II": TARIF_II,
    "III": TARIF_III,
    "IV_BIS": TARIF_IV_BIS,
    "V": TARIF_V,
    "VI": TARIF_VI,
    "VII": TARIF_VII,
    "VIII": TARIF_VIII,
    "IX": TARIF_IX,
    "X": TARIF_X,
}

# ─────────────────────────────────────────────────────────────
# Mapping des codes catégorie ASAC → clé de tarif du recueil
# ─────────────────────────────────────────────────────────────
# Le code ASAC est choisi par l'utilisateur dans le combo "Catégorie"
# (VP01, VP02, ...). Il faut le traduire en clé de tarif (I, II, ...).
MAPPING_CATEGORIE_VERS_TARIF = {
    "VP01": "I",        # Véhicule de tourisme (personne physique)
    "VP12": "I",        # Véhicule de tourisme (personne morale)
    "VP02": "II",       # Transport pour propre compte
    "VP03": "II",       # Transport public de marchandises
    "VP04": "IV_BIS",   # Transport public de voyageurs
    "VP05": "V",        # Véhicule motorisé 2/3 roues
    "VP06": "VI",       # Véhicule des garagistes
    "VP07": "VII",      # Véhicule d'auto-écoles
    "VP08": "VIII",     # Véhicule de location
    "VP09": "IX",       # Engin de chantier
    "VP10": "X",        # Véhicules spéciaux
    "VP11": "I",        # Catégorie 11 → fallback Tarif I
}