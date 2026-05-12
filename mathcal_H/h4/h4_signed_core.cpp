#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr std::uint64_t TOTAL_POINTS = 10460353203ULL; // 3^21

struct Metrics {
    int rawI = 0;
    int rawB = 0;
    int rawH = 0;
    int H_tot = 0;
    int H_pos = 0;
    int H_neg_abs = 0;
    int N_neg = 0;
    int h_loc_min = 999;
    int h_loc_max = -999;
    int H_blocks[5] = {0, 0, 0, 0, 0};
};

struct PairStats {
    std::uint64_t count = 0;
    std::uint64_t first_index = 0;
    std::string first_word;
    Metrics first_metrics;
    int min_H_pos = std::numeric_limits<int>::max();
    int max_H_pos = std::numeric_limits<int>::min();
    int min_H_neg_abs = std::numeric_limits<int>::max();
    int max_H_neg_abs = std::numeric_limits<int>::min();
    int min_h_loc_min = std::numeric_limits<int>::max();
    int max_h_loc_min = std::numeric_limits<int>::min();
    int min_h_loc_max = std::numeric_limits<int>::max();
    int max_h_loc_max = std::numeric_limits<int>::min();
};

struct Witness {
    std::uint64_t index = 0;
    std::string word;
    Metrics metrics;
};

struct RangeStats {
    std::uint64_t start = 0;
    std::uint64_t end = 0;
    std::uint64_t points = 0;
    double seconds = 0.0;
    int pair_min_rawH = 1171;
    int witness_min_rawH = 1217;
    std::uint64_t witness_limit = 100000;

    int min_rawH = std::numeric_limits<int>::max();
    int max_rawH = std::numeric_limits<int>::min();
    std::uint64_t min_count = 0;
    std::uint64_t max_count = 0;
    std::uint64_t min_index = 0;
    std::uint64_t max_index = 0;
    std::string min_word;
    std::string max_word;
    Metrics min_metrics;
    Metrics max_metrics;

    std::uint64_t high_points = 0;
    std::uint64_t high_pure_points = 0;
    std::uint64_t high_impure_points = 0;
    std::uint64_t witness_overflow = 0;
    std::map<std::pair<int, int>, PairStats> pairs;
    std::vector<Witness> witnesses;
};

int mod3(int v) {
    v %= 3;
    return v < 0 ? v + 3 : v;
}

int comp(int a, int e) {
    return mod3(-a - e);
}

int m_idx(int s, int a, int e) {
    return mod3(s) * 9 + mod3(a) * 3 + mod3(e);
}

int block_index(int b, int t) {
    if (b == 0 && t == 0) return 0;      // RRR
    if (b == 0) return 1;                // RRS
    if (t == 0) return 2;                // RSR
    if (t == b) return 3;                // SRR
    return 4;                            // DIST
}

void index_to_word(std::uint64_t index, std::array<unsigned char, 21>& x) {
    for (int i = 20; i >= 0; --i) {
        x[static_cast<std::size_t>(i)] = static_cast<unsigned char>(index % 3);
        index /= 3;
    }
}

void increment_word(std::array<unsigned char, 21>& x) {
    for (int i = 20; i >= 0; --i) {
        unsigned char next = static_cast<unsigned char>(x[static_cast<std::size_t>(i)] + 1);
        if (next < 3) {
            x[static_cast<std::size_t>(i)] = next;
            return;
        }
        x[static_cast<std::size_t>(i)] = 0;
    }
}

std::string word_to_string(const std::array<unsigned char, 21>& x) {
    std::string out;
    out.reserve(21);
    for (unsigned char v : x) out.push_back(static_cast<char>('0' + v));
    return out;
}

std::array<unsigned char, 21> parse_word(const std::string& word) {
    if (word.size() != 21) throw std::runtime_error("--word must have length 21");
    std::array<unsigned char, 21> x{};
    for (std::size_t i = 0; i < 21; ++i) {
        if (word[i] < '0' || word[i] > '2') throw std::runtime_error("--word may contain only 0,1,2");
        x[i] = static_cast<unsigned char>(word[i] - '0');
    }
    return x;
}

Metrics evaluate_word(const std::array<unsigned char, 21>& x) {
    int M[27];
    for (int a = 0; a < 3; ++a) {
        for (int e = 0; e < 3; ++e) {
            M[m_idx(0, a, e)] = (a == e) ? x[18 + a] : comp(a, e);
            M[m_idx(1, a, e)] = x[3 * a + e];
            M[m_idx(2, a, e)] = x[9 + 3 * a + e];
        }
    }

    int L[3][9];
    for (int c = 0; c < 3; ++c) {
        for (int u = 0; u < 3; ++u) {
            for (int ell = 0; ell < 3; ++ell) {
                L[c][3 * u + ell] = M[m_idx(u, c, ell)];
            }
        }
    }

    int K[27][9];
    for (int s = 0; s < 3; ++s) {
        for (int alpha = 0; alpha < 3; ++alpha) {
            for (int z = 0; z < 3; ++z) {
                int gi = 9 * s + 3 * alpha + z;
                for (int u = 0; u < 3; ++u) {
                    for (int ell = 0; ell < 3; ++ell) {
                        int inner = M[m_idx(u - s, z - s, ell - s)];
                        int second = mod3(s + inner);
                        K[gi][3 * u + ell] = M[m_idx(s, alpha, second)];
                    }
                }
            }
        }
    }

    int DL[3][3];
    for (int c = 0; c < 3; ++c) {
        for (int cp = 0; cp < 3; ++cp) {
            int d = 0;
            for (int pi = 0; pi < 9; ++pi) d += (L[c][pi] != L[cp][pi]);
            DL[c][cp] = d;
        }
    }

    Metrics m;
    int h_sum = 0;
    int h_pos_sum = 0;
    int h_neg_abs_sum = 0;
    int n_neg = 0;
    int block_sums[5] = {0, 0, 0, 0, 0};

    for (int b = 0; b < 3; ++b) {
        for (int t = 0; t < 3; ++t) {
            for (int a = 0; a < 3; ++a) {
                for (int e = 0; e < 3; ++e) {
                    for (int f = 0; f < 3; ++f) {
                        int xy = M[m_idx(b, a, e)];
                        int yz = M[m_idx(t - b, e - b, f - b)];
                        int zR = mod3(b + yz);
                        int epL = M[m_idx(t, xy, f)];
                        int epR = M[m_idx(b, a, zR)];
                        int dB = DL[epL][epR];
                        int g1 = 9 * mod3(t) + 3 * xy + mod3(f);
                        int g2 = 9 * mod3(b) + 3 * mod3(a) + zR;
                        int dI = 0;
                        for (int pi = 0; pi < 9; ++pi) dI += (K[g1][pi] != K[g2][pi]);
                        int h = 2 * (dI - dB);

                        m.rawI += dI;
                        m.rawB += dB;
                        h_sum += h;
                        if (h > 0) h_pos_sum += h;
                        if (h < 0) {
                            h_neg_abs_sum += -h;
                            ++n_neg;
                        }
                        if (h < m.h_loc_min) m.h_loc_min = h;
                        if (h > m.h_loc_max) m.h_loc_max = h;
                        block_sums[block_index(b, t)] += h;
                    }
                }
            }
        }
    }

    m.rawH = m.rawI - m.rawB;
    m.H_tot = 6 * m.rawH;
    m.H_pos = 3 * h_pos_sum;
    m.H_neg_abs = 3 * h_neg_abs_sum;
    m.N_neg = 3 * n_neg;
    for (int i = 0; i < 5; ++i) m.H_blocks[i] = 3 * block_sums[i];
    return m;
}

std::string metrics_json(const Metrics& m) {
    std::ostringstream os;
    os << "{";
    os << "\"rawI\":" << m.rawI;
    os << ",\"rawB\":" << m.rawB;
    os << ",\"rawH\":" << m.rawH;
    os << ",\"H_tot\":" << m.H_tot;
    os << ",\"H_pos\":" << m.H_pos;
    os << ",\"H_neg_abs\":" << m.H_neg_abs;
    os << ",\"N_neg\":" << m.N_neg;
    os << ",\"h_loc_min\":" << m.h_loc_min;
    os << ",\"h_loc_max\":" << m.h_loc_max;
    os << ",\"H_RRR\":" << m.H_blocks[0];
    os << ",\"H_RRS\":" << m.H_blocks[1];
    os << ",\"H_RSR\":" << m.H_blocks[2];
    os << ",\"H_SRR\":" << m.H_blocks[3];
    os << ",\"H_DIST\":" << m.H_blocks[4];
    os << "}";
    return os.str();
}

void update_pair(PairStats& ps, std::uint64_t index, const std::string& word, const Metrics& m) {
    if (ps.count == 0) {
        ps.first_index = index;
        ps.first_word = word;
        ps.first_metrics = m;
    }
    ++ps.count;
    if (m.H_pos < ps.min_H_pos) ps.min_H_pos = m.H_pos;
    if (m.H_pos > ps.max_H_pos) ps.max_H_pos = m.H_pos;
    if (m.H_neg_abs < ps.min_H_neg_abs) ps.min_H_neg_abs = m.H_neg_abs;
    if (m.H_neg_abs > ps.max_H_neg_abs) ps.max_H_neg_abs = m.H_neg_abs;
    if (m.h_loc_min < ps.min_h_loc_min) ps.min_h_loc_min = m.h_loc_min;
    if (m.h_loc_min > ps.max_h_loc_min) ps.max_h_loc_min = m.h_loc_min;
    if (m.h_loc_max < ps.min_h_loc_max) ps.min_h_loc_max = m.h_loc_max;
    if (m.h_loc_max > ps.max_h_loc_max) ps.max_h_loc_max = m.h_loc_max;
}

RangeStats evaluate_range(
    std::uint64_t start,
    std::uint64_t end,
    int pair_min_rawH,
    int witness_min_rawH,
    std::uint64_t witness_limit
) {
    if (end < start) throw std::runtime_error("--end must be >= --start");
    if (end > TOTAL_POINTS) throw std::runtime_error("--end exceeds 3^21");

    RangeStats st;
    st.start = start;
    st.end = end;
    st.points = end - start;
    st.pair_min_rawH = pair_min_rawH;
    st.witness_min_rawH = witness_min_rawH;
    st.witness_limit = witness_limit;

    std::array<unsigned char, 21> x{};
    index_to_word(start, x);

    auto t0 = std::chrono::steady_clock::now();
    for (std::uint64_t idx = start; idx < end; ++idx) {
        Metrics m = evaluate_word(x);
        std::string word;

        if (m.rawH < st.min_rawH) {
            st.min_rawH = m.rawH;
            st.min_count = 1;
            st.min_index = idx;
            word = word_to_string(x);
            st.min_word = word;
            st.min_metrics = m;
        } else if (m.rawH == st.min_rawH) {
            ++st.min_count;
        }
        if (m.rawH > st.max_rawH) {
            st.max_rawH = m.rawH;
            st.max_count = 1;
            st.max_index = idx;
            if (word.empty()) word = word_to_string(x);
            st.max_word = word;
            st.max_metrics = m;
        } else if (m.rawH == st.max_rawH) {
            ++st.max_count;
        }

        if (m.rawH >= pair_min_rawH) {
            if (word.empty()) word = word_to_string(x);
            ++st.high_points;
            if (m.N_neg == 0) {
                ++st.high_pure_points;
            } else {
                ++st.high_impure_points;
            }
            update_pair(st.pairs[std::make_pair(m.rawH, m.N_neg)], idx, word, m);
        }

        if (m.rawH >= witness_min_rawH) {
            if (word.empty()) word = word_to_string(x);
            if (st.witnesses.size() < witness_limit) {
                st.witnesses.push_back(Witness{idx, word, m});
            } else {
                ++st.witness_overflow;
            }
        }

        increment_word(x);
    }
    auto t1 = std::chrono::steady_clock::now();
    st.seconds = std::chrono::duration<double>(t1 - t0).count();
    return st;
}

std::string pair_json(const std::pair<const std::pair<int, int>, PairStats>& item) {
    int rawH = item.first.first;
    int N_neg = item.first.second;
    const PairStats& ps = item.second;
    std::ostringstream os;
    os << "{";
    os << "\"rawH\":" << rawH;
    os << ",\"H_tot\":" << 6 * rawH;
    os << ",\"N_neg\":" << N_neg;
    os << ",\"count\":" << ps.count;
    os << ",\"first_index\":" << ps.first_index;
    os << ",\"first_word\":\"" << ps.first_word << "\"";
    os << ",\"min_H_pos\":" << ps.min_H_pos;
    os << ",\"max_H_pos\":" << ps.max_H_pos;
    os << ",\"min_H_neg_abs\":" << ps.min_H_neg_abs;
    os << ",\"max_H_neg_abs\":" << ps.max_H_neg_abs;
    os << ",\"min_h_loc_min\":" << ps.min_h_loc_min;
    os << ",\"max_h_loc_min\":" << ps.max_h_loc_min;
    os << ",\"min_h_loc_max\":" << ps.min_h_loc_max;
    os << ",\"max_h_loc_max\":" << ps.max_h_loc_max;
    os << ",\"first_metrics\":" << metrics_json(ps.first_metrics);
    os << "}";
    return os.str();
}

std::string witness_json(const Witness& w) {
    std::ostringstream os;
    os << "{";
    os << "\"index\":" << w.index;
    os << ",\"word\":\"" << w.word << "\"";
    os << ",\"metrics\":" << metrics_json(w.metrics);
    os << "}";
    return os.str();
}

std::string range_json(const RangeStats& st) {
    std::ostringstream os;
    os << "{";
    os << "\"start\":" << st.start;
    os << ",\"end\":" << st.end;
    os << ",\"points\":" << st.points;
    os << ",\"seconds\":" << st.seconds;
    os << ",\"pair_min_rawH\":" << st.pair_min_rawH;
    os << ",\"witness_min_rawH\":" << st.witness_min_rawH;
    os << ",\"witness_limit\":" << st.witness_limit;
    os << ",\"min_rawH\":" << st.min_rawH;
    os << ",\"max_rawH\":" << st.max_rawH;
    os << ",\"min_H_tot\":" << 6 * st.min_rawH;
    os << ",\"max_H_tot\":" << 6 * st.max_rawH;
    os << ",\"min_count\":" << st.min_count;
    os << ",\"max_count\":" << st.max_count;
    os << ",\"min_index\":" << st.min_index;
    os << ",\"max_index\":" << st.max_index;
    os << ",\"min_word\":\"" << st.min_word << "\"";
    os << ",\"max_word\":\"" << st.max_word << "\"";
    os << ",\"min_metrics\":" << metrics_json(st.min_metrics);
    os << ",\"max_metrics\":" << metrics_json(st.max_metrics);
    os << ",\"high_points\":" << st.high_points;
    os << ",\"high_pure_points\":" << st.high_pure_points;
    os << ",\"high_impure_points\":" << st.high_impure_points;
    os << ",\"pair_count\":" << st.pairs.size();
    os << ",\"witness_count\":" << st.witnesses.size();
    os << ",\"witness_overflow\":" << st.witness_overflow;
    os << ",\"pairs\":[";
    bool first = true;
    for (const auto& item : st.pairs) {
        if (!first) os << ",";
        first = false;
        os << pair_json(item);
    }
    os << "]";
    os << ",\"witnesses\":[";
    first = true;
    for (const Witness& w : st.witnesses) {
        if (!first) os << ",";
        first = false;
        os << witness_json(w);
    }
    os << "]";
    os << "}";
    return os.str();
}

std::uint64_t parse_u64(const std::string& s) {
    std::size_t pos = 0;
    unsigned long long v = std::stoull(s, &pos, 10);
    if (pos != s.size()) throw std::runtime_error("invalid integer: " + s);
    return static_cast<std::uint64_t>(v);
}

int parse_i32(const std::string& s) {
    std::size_t pos = 0;
    int v = std::stoi(s, &pos, 10);
    if (pos != s.size()) throw std::runtime_error("invalid integer: " + s);
    return v;
}

void usage() {
    std::cerr
        << "Usage:\n"
        << "  h4_signed_core --word X21\n"
        << "  h4_signed_core --start N --end M [--pair-min-rawH 1171] [--witness-min-rawH 1217] [--witness-limit 100000]\n";
}

} // namespace

int main(int argc, char** argv) {
    try {
        std::string word;
        std::uint64_t start = 0;
        std::uint64_t end = 0;
        bool have_range = false;
        int pair_min_rawH = 1171;
        int witness_min_rawH = 1217;
        std::uint64_t witness_limit = 100000;

        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            auto need_value = [&](const char* name) -> std::string {
                if (i + 1 >= argc) throw std::runtime_error(std::string("missing value for ") + name);
                return argv[++i];
            };
            if (arg == "--word") {
                word = need_value("--word");
            } else if (arg == "--start") {
                start = parse_u64(need_value("--start"));
                have_range = true;
            } else if (arg == "--end") {
                end = parse_u64(need_value("--end"));
                have_range = true;
            } else if (arg == "--pair-min-rawH") {
                pair_min_rawH = parse_i32(need_value("--pair-min-rawH"));
            } else if (arg == "--witness-min-rawH") {
                witness_min_rawH = parse_i32(need_value("--witness-min-rawH"));
            } else if (arg == "--witness-limit") {
                witness_limit = parse_u64(need_value("--witness-limit"));
            } else if (arg == "--total") {
                std::cout << TOTAL_POINTS << "\n";
                return 0;
            } else if (arg == "--help" || arg == "-h") {
                usage();
                return 0;
            } else {
                throw std::runtime_error("unknown argument: " + arg);
            }
        }

        if (!word.empty()) {
            auto x = parse_word(word);
            Metrics m = evaluate_word(x);
            std::cout << "{\"word\":\"" << word << "\",\"metrics\":" << metrics_json(m) << "}\n";
            return 0;
        }

        if (!have_range) {
            usage();
            return 2;
        }
        RangeStats st = evaluate_range(start, end, pair_min_rawH, witness_min_rawH, witness_limit);
        std::cout << range_json(st) << "\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "ERROR " << ex.what() << "\n";
        return 1;
    }
}
