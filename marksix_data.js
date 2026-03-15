/**
 * Historical frequency data for HK Mark Six
 * Last Updated: March 2026
 * Source: nfd.com.tw (1976 - Present)
 */
const DATA_META = {
    lastUpdate: "March 2026",
    lastDrawDate: "2026-03-12",
    period: "1976 — Present",
    totalDraws: "Calculated with results up to 2026-03-12"
};

const HIST_FREQ = {
     1: 975,  2: 899,  3: 906,  4: 942,  5: 904,  6: 936,  7: 932,
     8: 956,  9: 933, 10: 950, 11: 908, 12: 963, 13: 918, 14: 955,
    15: 941, 16: 898, 17: 908, 18: 871, 19: 901, 20: 938, 21: 922,
    22: 970, 23: 895, 24: 954, 25: 855, 26: 924, 27: 957, 28: 948,
    29: 957, 30: 988, 31: 909, 32: 906, 33: 972, 34: 953, 35: 950,
    36: 934, 37: 788, 38: 784, 39: 777, 40: 770, 41: 661, 42: 687,
    43: 613, 44: 650, 45: 653, 46: 549, 47: 540, 48: 453, 49: 512
};

// Recent hot numbers (automatically updated)
const HOT_NUMS  = [30, 1, 33, 22, 12, 27, 29, 8, 14, 24, 34, 10];
// Cold numbers (automatically updated)
const COLD_NUMS = [18, 25, 37, 38, 39, 40, 42, 41, 45, 44, 43, 46, 47, 49, 48];

// Ball Color Configuration
const BALL_COLORS = {
    "red": [
        1,
        2,
        7,
        8,
        12,
        13,
        18,
        19,
        23,
        24,
        29,
        30,
        34,
        35,
        40,
        45,
        46
    ],
    "blue": [
        3,
        4,
        9,
        10,
        14,
        15,
        20,
        25,
        26,
        31,
        36,
        37,
        41,
        42,
        47,
        48
    ],
    "green": [
        5,
        6,
        11,
        16,
        17,
        21,
        22,
        27,
        28,
        32,
        33,
        38,
        39,
        43,
        44,
        49
    ]
};
