#include <algorithm>
#include <array>
#include <chrono>
#include <climits>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;
static inline int mod3(int x){ x%=3; if(x<0)x+=3; return x; }
static inline int comp3(int a,int b){ return mod3(-a-b); }
struct TermSpec{int b,t,a,e,f,label;};
vector<TermSpec> TERMS;

string coord_label(int c){ if(c<9){return string("A")+char('0'+c/3)+char('0'+c%3);} if(c<18){int k=c-9; return string("B")+char('0'+k/3)+char('0'+k%3);} return string("d")+char('0'+c-18); }
int coord_m(int b,int a,int e){ b=mod3(b); a=mod3(a); e=mod3(e); if(b==0){ if(a==e) return 18+a; return -1; } if(b==1) return 3*a+e; return 9+3*a+e; }
vector<int> possible_m_values_from_coord(int coord){ if(coord<0) return {}; return {0,1,2}; }

struct TermTable{
    vector<int> coords;
    unordered_map<int,int> pos;
    int rows=0, words=0;
    vector<unsigned long long> allmask, satmask, notsatmask;
    vector<array<vector<unsigned long long>,3>> valmask; // [pos][value]
};

int get_coord_val(const vector<int>& full, int coord){ return full[coord]; }
int mval_full(const vector<int>& full,int b,int a,int e){ b=mod3(b); a=mod3(a); e=mod3(e); if(b==0){ if(a==e) return full[18+a]; return comp3(a,e);} if(b==1) return full[3*a+e]; return full[9+3*a+e]; }
bool eval_term_full(const TermSpec& T,const vector<int>& full){
    int xy=mval_full(full,T.b,T.a,T.e);
    int lhs=mval_full(full,T.t,xy,T.f);
    int yz=mval_full(full,mod3(T.t-T.b),mod3(T.e-T.b),mod3(T.f-T.b));
    int rhs=mval_full(full,T.b,T.a,mod3(T.b+yz));
    return lhs==rhs;
}

vector<int> support_term(const TermSpec& T){
    set<int> s;
    auto add=[&](int c){ if(c>=0) s.insert(c); };
    int cxy=coord_m(T.b,T.a,T.e); add(cxy);
    vector<int> xyvals;
    if(cxy<0) xyvals={ (T.b==0 && T.a!=T.e) ? comp3(T.a,T.e) : 0 }; // only constant case possible here
    else xyvals={0,1,2};
    for(int xy:xyvals) add(coord_m(T.t,xy,T.f));
    int cyz=coord_m(mod3(T.t-T.b),mod3(T.e-T.b),mod3(T.f-T.b)); add(cyz);
    vector<int> yzvals;
    if(cyz<0) yzvals={ comp3(mod3(T.e-T.b),mod3(T.f-T.b)) };
    else yzvals={0,1,2};
    for(int yz:yzvals) add(coord_m(T.b,T.a,mod3(T.b+yz)));
    return vector<int>(s.begin(),s.end());
}

void setbit(vector<unsigned long long>& m,int idx){ m[idx>>6] |= 1ULL<<(idx&63); }
bool any_intersect(const vector<unsigned long long>& a,const vector<unsigned long long>& b){ for(size_t i=0;i<a.size();i++) if(a[i]&b[i]) return true; return false; }
bool subset_of(const vector<unsigned long long>& a,const vector<unsigned long long>& b){ for(size_t i=0;i<a.size();i++) if(a[i] & ~b[i]) return false; return true; }
bool mask_empty(const vector<unsigned long long>& a){ for(auto x:a) if(x) return false; return true; }

TermTable build_table(const TermSpec& T){
    TermTable tt; tt.coords=support_term(T); for(int i=0;i<(int)tt.coords.size();i++) tt.pos[tt.coords[i]]=i;
    int k=tt.coords.size(); tt.rows=1; for(int i=0;i<k;i++) tt.rows*=3; tt.words=(tt.rows+63)/64;
    tt.allmask.assign(tt.words,0); tt.satmask.assign(tt.words,0); tt.notsatmask.assign(tt.words,0);
    tt.valmask.resize(k); for(int p=0;p<k;p++) for(int v=0;v<3;v++) tt.valmask[p][v].assign(tt.words,0);
    vector<int> full(21,0);
    for(int code=0; code<tt.rows; code++){
        int tmp=code;
        for(int p=0;p<k;p++){ int v=tmp%3; tmp/=3; full[tt.coords[p]]=v; tt.valmask[p][v][code>>6] |= 1ULL<<(code&63); }
        setbit(tt.allmask,code);
        bool sat=eval_term_full(T,full);
        if(sat) setbit(tt.satmask,code); else setbit(tt.notsatmask,code);
    }
    return tt;
}

struct Solver{
    vector<TermTable> tabs;
    vector<vector<int>> terms_by_coord;
    vector<vector<unsigned long long>> curmask;
    array<int,21> asg;
    long long nodes=0, prunes=0, leaves=0, solutions=0;
    long long node_limit=1000000;
    chrono::steady_clock::time_point t0;
    double time_limit=30.0;
    bool timeout=false;
    array<int,21> found{};
    Solver(const vector<TermTable>& t):tabs(t){
        terms_by_coord.assign(21,{}); curmask.resize(tabs.size());
        for(int ti=0;ti<(int)tabs.size();ti++){
            curmask[ti]=tabs[ti].allmask;
            for(int c:tabs[ti].coords) terms_by_coord[c].push_back(ti);
        }
        asg.fill(-1); found.fill(-1);
    }
    pair<int,int> bounds(){ // forced_sat, possible_sat_count
        int forced_sat=0, possible_sat=0;
        for(int ti=0;ti<(int)tabs.size();ti++){
            auto &m=curmask[ti], &sat=tabs[ti].satmask;
            bool can_sat=any_intersect(m,sat);
            if(can_sat) possible_sat++;
            if(subset_of(m,sat)) forced_sat++;
        }
        return {forced_sat, possible_sat};
    }
    int exact_count(){ int c=0; for(int ti=0;ti<(int)tabs.size();ti++) if(subset_of(curmask[ti],tabs[ti].satmask)) c++; return c; }
    struct Change{int ti; vector<unsigned long long> old;};
    void apply(int var,int val, vector<Change>& trail){
        asg[var]=val;
        for(int ti: terms_by_coord[var]){
            auto it=tabs[ti].pos.find(var); if(it==tabs[ti].pos.end()) continue; int p=it->second;
            vector<unsigned long long> nm=curmask[ti];
            for(size_t w=0; w<nm.size(); w++) nm[w] &= tabs[ti].valmask[p][val][w];
            trail.push_back({ti,curmask[ti]});
            curmask[ti].swap(nm);
        }
    }
    void undo(int var, vector<Change>& trail){
        for(int i=(int)trail.size()-1;i>=0;i--) curmask[trail[i].ti].swap(trail[i].old);
        asg[var]=-1;
    }
    int choose_var_min(int target){
        int bestv=-1; int bestscore=-1;
        for(int v=0;v<21;v++) if(asg[v]<0){
            int minlb=999, sumlb=0, maxlb=-1; int changed=0;
            for(int val=0;val<3;val++){
                vector<Change> tr; apply(v,val,tr); auto [lb,ub]=bounds(); undo(v,tr);
                minlb=min(minlb,lb); maxlb=max(maxlb,lb); sumlb+=lb; if(lb>target) changed+=1000;
            }
            int score = minlb*100000 + sumlb*100 + maxlb + changed + (int)terms_by_coord[v].size();
            if(score>bestscore){bestscore=score; bestv=v;}
        }
        return bestv;
    }
    int choose_var_max(int target){
        int bestv=-1; int bestscore=INT_MAX;
        for(int v=0;v<21;v++) if(asg[v]<0){
            int maxub=-1, sumub=0, minub=999;
            for(int val=0;val<3;val++){
                vector<Change> tr; apply(v,val,tr); auto [lb,ub]=bounds(); undo(v,tr);
                maxub=max(maxub,ub); minub=min(minub,ub); sumub+=ub;
            }
            int score = maxub*100000 + sumub*100 + minub - (int)terms_by_coord[v].size();
            if(score<bestscore){bestscore=score; bestv=v;}
        }
        return bestv;
    }
    void dfs_min(int target){
        if(timeout) return;
        nodes++;
        if(nodes%10000==0){ double sec=chrono::duration<double>(chrono::steady_clock::now()-t0).count(); if(sec>time_limit || nodes>node_limit){timeout=true; return;} }
        auto [lb,ub]=bounds();
        if(lb>target){ prunes++; return; }
        bool complete=true; for(int v=0;v<21;v++) if(asg[v]<0){complete=false; break;}
        if(complete){ leaves++; int ex=exact_count(); if(ex<=target){ solutions++; found=asg; timeout=true; } return; }
        int var=choose_var_min(target);
        vector<pair<int,int>> order;
        for(int val=0;val<3;val++){ vector<Change> tr; apply(var,val,tr); auto [lb2,ub2]=bounds(); undo(var,tr); order.push_back({lb2,val}); }
        sort(order.begin(),order.end()); // low bound first to find counterexamples; exhaustive eventually all
        for(auto [sc,val]:order){ vector<Change> tr; apply(var,val,tr); dfs_min(target); undo(var,tr); if(timeout) return; }
    }
    void dfs_max(int target){
        if(timeout) return;
        nodes++;
        if(nodes%10000==0){ double sec=chrono::duration<double>(chrono::steady_clock::now()-t0).count(); if(sec>time_limit || nodes>node_limit){timeout=true; return;} }
        auto [lb,ub]=bounds();
        if(ub<target){ prunes++; return; }
        bool complete=true; for(int v=0;v<21;v++) if(asg[v]<0){complete=false; break;}
        if(complete){ leaves++; int ex=exact_count(); if(ex>=target){ solutions++; found=asg; timeout=true; } return; }
        int var=choose_var_max(target);
        vector<pair<int,int>> order;
        for(int val=0;val<3;val++){ vector<Change> tr; apply(var,val,tr); auto [lb2,ub2]=bounds(); undo(var,tr); order.push_back({-ub2,val}); }
        sort(order.begin(),order.end()); // high ub first
        for(auto [sc,val]:order){ vector<Change> tr; apply(var,val,tr); dfs_max(target); undo(var,tr); if(timeout) return; }
    }
    string found_string(){ string s=""; for(int i=0;i<21;i++){ if(i) s+=","; s+=to_string(found[i]); } return s; }
};

int main(int argc,char**argv){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string outdir="generated/f3_cert_extrema"; int minTarget=20, maxTarget=200; long long nodeLimit=200000; double timeLimit=20.0; string mode="both"; bool setupOnly=false;
    for(int i=1;i<argc;i++){ string a=argv[i]; if(a=="--outdir"&&i+1<argc) outdir=argv[++i]; else if(a=="--min-target"&&i+1<argc) minTarget=stoi(argv[++i]); else if(a=="--max-target"&&i+1<argc) maxTarget=stoi(argv[++i]); else if(a=="--node-limit"&&i+1<argc) nodeLimit=stoll(argv[++i]); else if(a=="--time-limit"&&i+1<argc) timeLimit=stod(argv[++i]); else if(a=="--mode"&&i+1<argc) mode=argv[++i]; else if(a=="--setup-only") setupOnly=true; }
    system(("mkdir -p '"+outdir+"'").c_str());
    for(int b=0;b<3;b++) for(int t=0;t<3;t++) for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){
        int label=(b==0&&t==0)?0:(b==0&&t!=0)?1:(b!=0&&t==0)?2:(b!=0&&t==b)?3:4;
        TERMS.push_back({b,t,a,e,f,label});
    }
    vector<TermTable> tabs; tabs.reserve(TERMS.size());
    map<int,int> supportDist; long long totalRows=0; int maxK=0;
    for(auto &T:TERMS){ tabs.push_back(build_table(T)); int k=tabs.back().coords.size(); supportDist[k]++; maxK=max(maxK,k); totalRows+=tabs.back().rows; }
    // variable participation
    vector<int> part(21,0); for(auto &tt:tabs) for(int c:tt.coords) part[c]++;
    ofstream csv(outdir+"/term_support_summary.csv"); csv<<"support_size,term_count\n"; for(auto &kv:supportDist) csv<<kv.first<<","<<kv.second<<"\n"; csv.close();
    ofstream vc(outdir+"/coordinate_participation.csv"); vc<<"coord,label,term_support_count\n"; for(int i=0;i<21;i++) vc<<i<<","<<coord_label(i)<<","<<part[i]<<"\n"; vc.close();
    auto write_setup_summary=[&](){
        ofstream js(outdir+"/f3_csp_setup_summary.json");
        js<<"{\n";
        js<<"  \"normalized_terms\": 243,\n";
        js<<"  \"variables_ternary\": 21,\n";
        js<<"  \"term_support_size_distribution\": {"; bool first=true; for(auto &kv:supportDist){ if(!first) js<<","; first=false; js<<"\""<<kv.first<<"\":"<<kv.second; } js<<"},\n";
        js<<"  \"max_support_size\": "<<maxK<<",\n";
        js<<"  \"total_local_truth_rows\": "<<totalRows<<"\n";
        js<<"}\n";
    };
    write_setup_summary();
    if(setupOnly) return 0;
    auto runone=[&](string tag,bool ismin,int target){
        Solver S(tabs); S.node_limit=nodeLimit; S.time_limit=timeLimit; S.t0=chrono::steady_clock::now();
        if(ismin) S.dfs_min(target); else S.dfs_max(target);
        double sec=chrono::duration<double>(chrono::steady_clock::now()-S.t0).count();
        ofstream js(outdir+"/"+tag+"_bb_summary.json");
        js<<"{\n";
        js<<"  \"mode\": \""<<(ismin?"min_raw_at_most":"max_raw_at_least")<<"\",\n";
        js<<"  \"target_raw\": "<<target<<",\n";
        js<<"  \"target_assoc\": "<<3*target<<",\n";
        js<<"  \"nodes\": "<<S.nodes<<",\n";
        js<<"  \"prunes\": "<<S.prunes<<",\n";
        js<<"  \"leaves\": "<<S.leaves<<",\n";
        js<<"  \"solutions_found\": "<<S.solutions<<",\n";
        js<<"  \"stopped_by_limit\": "<<(S.timeout?"true":"false")<<",\n";
        js<<"  \"seconds\": "<<fixed<<setprecision(6)<<sec<<",\n";
        js<<"  \"node_limit\": "<<nodeLimit<<",\n";
        js<<"  \"time_limit\": "<<timeLimit<<",\n";
        if(S.solutions) js<<"  \"found_x21\": ["<<S.found_string()<<"]\n"; else js<<"  \"found_x21\": null\n";
        js<<"}\n";
    };
    if(mode=="both"||mode=="min") runone("min_target",true,minTarget);
    if(mode=="both"||mode=="max") runone("max_target",false,maxTarget);
    write_setup_summary();
    return 0;
}
