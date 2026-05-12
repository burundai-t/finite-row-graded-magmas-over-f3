#include <algorithm>
#include <array>
#include <chrono>
#include <iostream>
#include <string>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif
using namespace std;
static inline int mod3(int x){ x%=3; return x<0?x+3:x; }
static inline int comp3(int a,int b){ return (6-a-b)%3; }
static inline int idx(int a,int e){ return 3*a+e; }

struct Kernel {
    static constexpr int N = 19683;
    int d[3]{};
    unsigned char M0[9]{};
    vector<array<unsigned char,9>> vals;
    array<vector<unsigned char>,9> coord;
    vector<unsigned char> FA, FB;
    int base=0;
    Kernel(const string& ds){
        for(int i=0;i<3;i++) d[i]=ds[i]-'0';
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) M0[idx(a,e)] = (a==e)?d[a]:comp3(a,e);
        vals.resize(N);
        for(int j=0;j<9;j++) coord[j].resize(N);
        for(int n=0;n<N;n++){
            int x=n;
            for(int i=0;i<9;i++){ unsigned char v=x%3; x/=3; vals[n][i]=v; coord[i][n]=v; }
        }
        FA.assign(N,0); FB.assign(N,0); precompute();
    }
    inline unsigned char m0(int a,int e) const { return M0[idx(a,e)]; }
    int block00() const { int r=0; for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=m0(a,e), lhs=m0(xy,f), yz=m0(e,f), rhs=m0(a,yz); r+=(lhs==rhs);} return r; }
    int block01_A(const unsigned char* A) const { int r=0; for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=m0(a,e), lhs=A[idx(xy,f)], yz=A[idx(e,f)], rhs=m0(a,yz); r+=(lhs==rhs);} return r; }
    int block02_B(const unsigned char* B) const { int r=0; for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=m0(a,e), lhs=B[idx(xy,f)], yz=B[idx(e,f)], rhs=m0(a,yz); r+=(lhs==rhs);} return r; }
    int block11_A(const unsigned char* A) const { int r=0; for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=A[idx(a,e)], lhs=A[idx(xy,f)], yz=m0(mod3(e-1),mod3(f-1)), rhs=A[idx(a,mod3(1+yz))]; r+=(lhs==rhs);} return r; }
    int block22_B(const unsigned char* B) const { int r=0; for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=B[idx(a,e)], lhs=B[idx(xy,f)], yz=m0(mod3(e-2),mod3(f-2)), rhs=B[idx(a,mod3(2+yz))]; r+=(lhs==rhs);} return r; }
    void precompute(){ base=block00(); for(int n=0;n<N;n++){ const unsigned char* X=vals[n].data(); FA[n]=block01_A(X)+block11_A(X); FB[n]=block02_B(X)+block22_B(X); } }
    int direct_pair(int ia,int ib) const {
        const unsigned char *A=vals[ia].data(), *B=vals[ib].data();
        int r=base+FA[ia]+FB[ib];
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=A[idx(a,e)], lhs=m0(xy,f), yz=B[idx(mod3(e-1),mod3(f-1))], rhs=A[idx(a,mod3(1+yz))]; r+=(lhs==rhs); }
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=A[idx(a,e)], lhs=B[idx(xy,f)], yz=A[idx(mod3(e-1),mod3(f-1))], rhs=A[idx(a,mod3(1+yz))]; r+=(lhs==rhs); }
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=B[idx(a,e)], lhs=m0(xy,f), yz=A[idx(mod3(e-2),mod3(f-2))], rhs=B[idx(a,mod3(2+yz))]; r+=(lhs==rhs); }
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){ int xy=B[idx(a,e)], lhs=A[idx(xy,f)], yz=B[idx(mod3(e-2),mod3(f-2))], rhs=B[idx(a,mod3(2+yz))]; r+=(lhs==rhs); }
        return r;
    }
    void process_A(int ia, array<unsigned long long,244>& hist, vector<unsigned short>& raw) const {
        const unsigned char* A=vals[ia].data(); int prefix=base+FA[ia];
        for(int ib=0; ib<N; ++ib) raw[ib]=(unsigned short)(prefix+FB[ib]);
        // b=1,t=0
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){
            unsigned char lhs=m0(A[idx(a,e)],f); const unsigned char* C=coord[idx(mod3(e-1),mod3(f-1))].data();
            unsigned char r0=A[idx(a,1)], r1=A[idx(a,2)], r2=A[idx(a,0)];
            for(int ib=0; ib<N; ++ib){ unsigned char z=C[ib]; unsigned char rhs = (z==0? r0 : (z==1? r1 : r2)); raw[ib] += (lhs==rhs); }
        }
        // b=1,t=2
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){
            const unsigned char* C=coord[idx(A[idx(a,e)],f)].data(); int yz=A[idx(mod3(e-1),mod3(f-1))]; unsigned char rhs=A[idx(a,mod3(1+yz))];
            for(int ib=0; ib<N; ++ib) raw[ib] += (C[ib]==rhs);
        }
        // b=2,t=0
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){
            const unsigned char* X=coord[idx(a,e)].data(); int yz=A[idx(mod3(e-2),mod3(f-2))]; const unsigned char* R=coord[idx(a,mod3(2+yz))].data();
            unsigned char m00=m0(0,f), m10=m0(1,f), m20=m0(2,f);
            for(int ib=0; ib<N; ++ib){ unsigned char x=X[ib]; unsigned char lhs=(x==0?m00:(x==1?m10:m20)); raw[ib] += (lhs==R[ib]); }
        }
        // b=2,t=1
        for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){
            const unsigned char* X=coord[idx(a,e)].data(); const unsigned char* Y=coord[idx(mod3(e-2),mod3(f-2))].data();
            unsigned char a0=A[idx(0,f)], a1=A[idx(1,f)], a2=A[idx(2,f)];
            const unsigned char* R0=coord[idx(a,2)].data(); const unsigned char* R1=coord[idx(a,0)].data(); const unsigned char* R2=coord[idx(a,1)].data();
            for(int ib=0; ib<N; ++ib){ unsigned char x=X[ib]; unsigned char lhs=(x==0?a0:(x==1?a1:a2)); unsigned char y=Y[ib]; unsigned char rhs=(y==0?R0[ib]:(y==1?R1[ib]:R2[ib])); raw[ib] += (lhs==rhs); }
        }
        for(int ib=0; ib<N; ++ib) hist[raw[ib]]++;
    }
};

int main(int argc,char** argv){
    string ds="000"; int threads=8; int maxA=19683; bool selftest=false;
    for(int i=1;i<argc;i++){ string a=argv[i]; if(a=="--d"&&i+1<argc) ds=argv[++i]; else if(a=="--threads"&&i+1<argc) threads=stoi(argv[++i]); else if(a=="--maxA"&&i+1<argc) maxA=stoi(argv[++i]); else if(a=="--selftest") selftest=true; else { cerr<<"bad arg "<<a<<"\n"; return 2; } }
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif
    auto t0=chrono::high_resolution_clock::now(); Kernel K(ds);
    if(selftest){ for(int ia: {0,1,123,7777,19682}){ array<unsigned long long,244> h{}; h.fill(0); vector<unsigned short> raw(K.N); K.process_A(ia,h,raw); for(int ib: {0,1,2,456,12345,19682}){ int r=K.direct_pair(ia,ib); if(raw[ib]!=r){ cerr<<"selftest fail d="<<ds<<" ia="<<ia<<" ib="<<ib<<" raw="<<raw[ib]<<" direct="<<r<<"\n"; return 2; } } } cerr<<"selftest OK d="<<ds<<"\n"; }
    int NA=min(19683,maxA); int nt=1;
#ifdef _OPENMP
    nt=omp_get_max_threads();
#endif
    vector<array<unsigned long long,244>> locals(nt); for(auto&h:locals) h.fill(0);
#pragma omp parallel
    {
        int tid=0;
#ifdef _OPENMP
        tid=omp_get_thread_num();
#endif
        vector<unsigned short> raw(K.N);
#pragma omp for schedule(static)
        for(int ia=0; ia<NA; ++ia) K.process_A(ia, locals[tid], raw);
    }
    array<unsigned long long,244> hist{}; hist.fill(0); for(auto&h:locals) for(int i=0;i<244;i++) hist[i]+=h[i];
    auto t1=chrono::high_resolution_clock::now(); double sec=chrono::duration<double>(t1-t0).count(); unsigned long long pts=0, checksum=0; for(int i=0;i<244;i++){ pts+=hist[i]; checksum+=hist[i]*(unsigned long long)i; }
    cerr<<"d "<<ds<<" maxA "<<NA<<" points "<<pts<<" sec "<<sec<<" pps "<<(pts/sec)<<" raw_checksum "<<checksum<<" threads "<<nt<<" base "<<K.base<<"\n";
    cout<<"raw,assoc,count\n"; for(int i=0;i<244;i++) if(hist[i]) cout<<i<<","<<3*i<<","<<hist[i]<<"\n";
    return 0;
}
