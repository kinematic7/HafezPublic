SURAH_NAMES: dict[str, int] = {
    # 1. Al-Fatihah
    "fatiha": 1, "al-fatiha": 1, "alfatiha": 1, "al-fatihah": 1, "fatihah": 1, "opening": 1,
    # 2. Al-Baqarah
    "baqarah": 2, "al-baqarah": 2, "albaqarah": 2, "cow": 2,
    # 3. Ali 'Imran
    "imran": 3, "ali 'imran": 3, "ali imran": 3, "al-imran": 3, "alimran": 3,
    # 4. An-Nisa
    "an-nisa": 4, "nisa": 4, "annisa": 4, "women": 4,
    # 5. Al-Ma'idah
    "al-maidah": 5, "maidah": 5, "al-ma'idah": 5, "table": 5,
    # 6. Al-An'am
    "al-an'am": 6, "al-anam": 6, "anam": 6, "cattle": 6,
    # 7. Al-A'raf
    "al-a'raf": 7, "al-araf": 7, "araf": 7,
    # 8. Al-Anfal
    "al-anfal": 8, "anfal": 8,
    # 9. At-Tawbah
    "at-tawbah": 9, "tawbah": 9, "repentance": 9,
    # 10. Yunus
    "yunus": 10, "yunas": 10,
    # 11. Hud
    "hud": 11,
    # 12. Yusuf
    "yusuf": 12, "joseph": 12,
    # 13. Ar-Ra'd
    "ar-ra'd": 13, "ar-rad": 13, "rad": 13, "thunder": 13,
    # 14. Ibrahim
    "ibrahim": 14, "abraham": 14,
    # 15. Al-Hijr
    "al-hijr": 15, "hijr": 15,
    # 16. An-Nahl
    "an-nahl": 16, "nahl": 16, "bee": 16,
    # 17. Al-Isra
    "al-isra": 17, "isra": 17,
    # 18. Al-Kahf
    "kahf": 18, "al-kahf": 18, "cave": 18,
    # 19. Maryam
    "maryam": 19, "mary": 19,
    # 20. Taha
    "taha": 20, "ta-ha": 20,
    # 21. Al-Anbiya
    "al-anbiya": 21, "anbiya": 21, "prophets": 21,
    # 22. Al-Hajj
    "al-hajj": 22, "hajj": 22, "pilgrimage": 22,
    # 23. Al-Mu'minun
    "al-mu'minun": 23, "al-muminun": 23, "muminun": 23,
    # 24. An-Nur
    "an-nur": 24, "nur": 24, "light": 24,
    # 25. Al-Furqan
    "al-furqan": 25, "furqan": 25,
    # 26. Ash-Shu'ara
    "ash-shu'ara": 26, "ash-shuara": 26, "shuara": 26, "poets": 26,
    # 27. An-Naml
    "an-naml": 27, "naml": 27, "ant": 27,
    # 28. Al-Qasas
    "al-qasas": 28, "qasas": 28,
    # 29. Al-'Ankabut
    "al-'ankabut": 29, "al-ankabut": 29, "ankabut": 29, "spider": 29,
    # 30. Ar-Rum
    "ar-rum": 30, "rum": 30, "romans": 30,
    # 31. Luqman
    "luqman": 31,
    # 32. As-Sajdah
    "as-sajdah": 32, "sajdah": 32, "prostration": 32,
    # 33. Al-Ahzab
    "al-ahzab": 33, "ahzab": 33,
    # 34. Saba
    "saba": 34, "sheba": 34,
    # 35. Fatir
    "fatir": 35,
    # 36. Ya-Sin
    "yasin": 36, "ya-sin": 36, "yaseen": 36,
    # 37. As-Saffat
    "as-saffat": 37, "saffat": 37,
    # 38. Sad
    "sad": 38,
    # 39. Az-Zumar
    "az-zumar": 39, "zumar": 39,
    # 40. Ghafir
    "ghafir": 40, "mumin": 40,
    # 41. Fussilat
    "fussilat": 41,
    # 42. Ash-Shura
    "ash-shura": 42, "shura": 42,
    # 43. Az-Zukhruf
    "az-zukhruf": 43, "zukhruf": 43,
    # 44. Ad-Dukhan
    "ad-dukhan": 44, "dukhan": 44, "smoke": 44,
    # 45. Al-Jathiyah
    "al-jathiyah": 45, "jathiyah": 45,
    # 46. Al-Ahqaf
    "al-ahqaf": 46, "ahqaf": 46,
    # 47. Muhammad
    "muhammad": 47,
    # 48. Al-Fath
    "al-fath": 48, "fath": 48, "victory": 48,
    # 49. Al-Hujurat
    "al-hujurat": 49, "hujurat": 49,
    # 50. Qaf
    "qaf": 50,
    # 51. Adh-Dhariyat
    "adh-dhariyat": 51, "dhariyat": 51,
    # 52. At-Tur
    "at-tur": 52, "tur": 52,
    # 53. An-Najm
    "an-najm": 53, "najm": 53, "star": 53,
    # 54. Al-Qamar
    "al-qamar": 54, "qamar": 54, "moon": 54,
    # 55. Ar-Rahman
    "ar-rahman": 55, "rahman": 55,
    # 56. Al-Waqi'ah
    "al-waqi'ah": 56, "al-waqiah": 56, "waqiah": 56,
    # 57. Al-Hadid
    "al-hadid": 57, "hadid": 57, "iron": 57,
    # 58. Al-Mujadila
    "al-mujadila": 58, "mujadila": 58,
    # 59. Al-Hashr
    "al-hashr": 59, "hashr": 59,
    # 60. Al-Mumtahanah
    "al-mumtahanah": 60, "mumtahanah": 60,
    # 61. As-Saff
    "as-saff": 61, "saff": 61,
    # 62. Al-Jumu'ah
    "al-jumu'ah": 62, "al-jumuah": 62, "jumuah": 62, "friday": 62,
    # 63. Al-Munafiqun
    "al-munafiqun": 63, "munafiqun": 63,
    # 64. At-Taghabun
    "at-taghabun": 64, "taghabun": 64,
    # 65. At-Talaq
    "at-talaq": 65, "talaq": 65, "divorce": 65,
    # 66. At-Tahrim
    "at-tahrim": 66, "tahrim": 66,
    # 67. Al-Mulk
    "al-mulk": 67, "mulk": 67, "sovereignty": 67,
    # 68. Al-Qalam
    "al-qalam": 68, "qalam": 68, "pen": 68,
    # 69. Al-Haqqah
    "al-haqqah": 69, "haqqah": 69,
    # 70. Al-Ma'arij
    "al-ma'arij": 70, "al-maarij": 70, "maarij": 70,
    # 71. Nuh
    "nuh": 71, "noah": 71,
    # 72. Al-Jinn
    "al-jinn": 72, "jinn": 72,
    # 73. Al-Muzzammil
    "al-muzzammil": 73, "muzzammil": 73,
    # 74. Al-Muddaththir
    "al-muddaththir": 74, "muddaththir": 74,
    # 75. Al-Qiyamah
    "al-qiyamah": 75, "qiyamah": 75, "resurrection": 75,
    # 76. Al-Insan
    "al-insan": 76, "insan": 76,
    # 77. Al-Mursalat
    "al-mursalat": 77, "mursalat": 77,
    # 78. An-Naba
    "an-naba": 78, "naba": 78,
    # 79. An-Nazi'at
    "an-nazi'at": 79, "an-naziat": 79, "naziat": 79,
    # 80. 'Abasa
    "'abasa": 80, "abasa": 80,
    # 81. At-Takwir
    "at-takwir": 81, "takwir": 81,
    # 82. Al-Infitar
    "al-infitar": 82, "infitar": 82,
    # 83. Al-Mutaffifin
    "al-mutaffifin": 83, "mutaffifin": 83,
    # 84. Al-Inshiqaq
    "al-inshiqaq": 84, "inshiqaq": 84,
    # 85. Al-Buruj
    "al-buruj": 85, "buruj": 85,
    # 86. At-Tariq
    "at-tariq": 86, "tariq": 86,
    # 87. Al-A'la
    "al-a'la": 87, "al-ala": 87, "ala": 87,
    # 88. Al-Ghashiyah
    "al-ghashiyah": 88, "ghashiyah": 88,
    # 89. Al-Fajr
    "al-fajr": 89, "fajr": 89, "dawn": 89,
    # 90. Al-Balad
    "al-balad": 90, "balad": 90, "city": 90,
    # 91. Ash-Shams
    "ash-shams": 91, "shams": 91, "sun": 91,
    # 92. Al-Layl
    "al-layl": 92, "layl": 92, "night": 92,
    # 93. Ad-Duha
    "ad-duha": 93, "duha": 93,
    # 94. Ash-Sharh
    "ash-sharh": 94, "sharh": 94, "inshirah": 94,
    # 95. At-Tin
    "at-tin": 95, "tin": 95, "fig": 95,
    # 96. Al-'Alaq
    "al-'alaq": 96, "al-alaq": 96, "alaq": 96,
    # 97. Al-Qadr
    "al-qadr": 97, "qadr": 97,
    # 98. Al-Bayyinah
    "al-bayyinah": 98, "bayyinah": 98,
    # 99. Az-Zalzalah
    "az-zalzalah": 99, "zalzalah": 99, "zilzal": 99,
    # 100. Al-'Adiyat
    "al-'adiyat": 100, "al-adiyat": 100, "adiyat": 100,
    # 101. Al-Qari'ah
    "al-qari'ah": 101, "al-qariah": 101, "qariah": 101,
    # 102. At-Takathur
    "at-takathur": 102, "takathur": 102,
    # 103. Al-'Asr
    "al-'asr": 103, "al-asr": 103, "asr": 103,
    # 104. Al-Humazah
    "al-humazah": 104, "humazah": 104,
    # 105. Al-Fil
    "al-fil": 105, "fil": 105, "elephant": 105,
    # 106. Quraysh
    "quraysh": 106,
    # 107. Al-Ma'un
    "al-ma'un": 107, "al-maun": 107, "maun": 107,
    # 108. Al-Kawthar
    "al-kawthar": 108, "kawthar": 108, "kauthar": 108,
    # 109. Al-Kafirun
    "al-kafirun": 109, "kafirun": 109,
    # 110. An-Nasr
    "an-nasr": 110, "nasr": 110,
    # 111. Al-Masad
    "al-masad": 111, "masad": 111, "lahab": 111,
    # 112. Al-Ikhlas
    "al-ikhlas": 112, "ikhlas": 112,
    # 113. Al-Falaq
    "al-falaq": 113, "falaq": 113,
    # 114. An-Nas
    "an-nas": 114, "nas": 114,
}