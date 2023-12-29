import numpy as np
import matplotlib.pyplot as plt
import math
import numpy.linalg as LA
from vasp import get_point

N = 20 #原子数
num_points = 5 #メッシュ
rprm = 4 #ホッピングは小数第3位まで
rcut = [50, 50, 50]

#FT行列計算用関数
def cal_FT(k_v, T):
    return np.exp(j*np.dot(k_v, T))

#基本並進ベクトルa,逆基本並進ベクトルbを取得
a=np.zeros((3,3), dtype = np.complex128)
b=np.zeros((3,3), dtype = np.complex128)
with open("scf/OUTCAR") as out:
    outcar=out.readlines()

for i,line in enumerate(outcar):
    if "  direct lattice vectors                    reciprocal lattice vectors"  in line:
        dd1=outcar[i+1].split()
        dd2=outcar[i+2].split()
        dd3=outcar[i+3].split()
for i in range(3):
    a[0,i]=float(dd1[i])
    a[1,i]=float(dd2[i])
    a[2,i]=float(dd3[i])
    b[0,i]=float(dd1[i])
    b[1,i]=float(dd2[i])
    b[2,i]=float(dd3[i])
print("a=",a)
print("b=",b, "\n")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#格子ベクトルTのリストを作る

#aの係数nを取得する
mainham=open("mainham",mode="w")
wn=[] #1,2 etc.
with open("wannier90_hr.dat") as f:
    for i,line in enumerate(f):
        dam=line.split()
        if i==0:
            writtentime=dam[2]+dam[3]+dam[4]
        elif i==1:
            nw=int(dam[0])
        elif i==2:
            num_sites=int(dam[0])
        elif i < math.ceil(num_sites/15)+3: #+3→開始位置分
            for value in dam:
                wn.append(value)
        else:
            mainham.write(line) #mainham書き込み
mainham.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#k_vを計算

#vasp.pyから座標取得
points=get_point()
print("points=",points)

#波数lのリストを作る
l_lists=[]
for i in range(len(points)-1):
    lx=np.linspace(points[i][1],points[i+1][1],num_points)
    ly=np.linspace(points[i][2],points[i+1][2],num_points)
    lz=np.linspace(points[i][3],points[i+1][3],num_points)
    for j in range(num_points):
        l_list=[lx[j]/N,ly[j]/N,lz[j]/N]
        l_lists.append(l_list)
#波数ベクトルkのリストを作る
k_v=[]
for i in range(len(l_lists)):
    k=np.dot(l_lists[i],b)
    k_v.append(k)
#print("k_v=",k_v)
#print("len(k_v)=", len(k_v))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#mainham_wnから各値を取得し固有値計算

#ホッピングの値を整形してmainham_wnを生成
mainham_wn = open("mainham_wn",mode="w") 
with  open("mainham") as f:
    for i,line in enumerate(f):
        dam = line.split()
        dam[5] = round(float(dam[5]) / float(wn[int(i / (nw**2))]), rprm)
        dam[6] = round(float(dam[6]) / float(wn[int(i / (nw**2))]), rprm)
        mainham_wn.write("   "+dam[0]+"    "+dam[1]+"    "+dam[2]+"    "+dam[3]+"    "+dam[4]+"    "+str(dam[5])+"    "+str(dam[6])+"\n")        
mainham_wn.close()
#ハミルトニアンのリストを作る
T_lists = [] #格子ベクトルのリスト
H = np.zeros((nw, nw), dtype = np.complex128)
H_lists = []
count = 0 #ハミルトニアンの区切りをつけるためのカウント
with open ("mainham_wn") as f:
        for i, line in enumerate(f):
            dam = line.split()
            n = np.array([float(dam[0]), float(dam[1]),float(dam[2])])
            T = np.dot(a,n)               
            T_lists.append(T)
#カットオフ設定
            lenx = np.sqrt(T[0]*T[0])
            leny = np.sqrt(T[1]*T[1])
            lenz = np.sqrt(T[2]*T[2])
            if (lenx >= rcut[0]) or (leny >= rcut[1]) or (lenz >= rcut[2]) :
                fac = 0.0
            else :
                fac = 1.0
            H[int(dam[3])-1, int(dam[4])-1] = complex(float(dam[5]) * fac, float(dam[6]) * fac)
            count += 1
            if count == nw ** 2:
                H_lists.append(H)
                count = 0
mainham_wn.close()
#固有値計算
H_sum = np.zeros((nw,nw), dtype = np.complex128)
ene = []
count = 0
print("len(k_v)",len(k_v))
for i in range (2):
    for j in range(len(H_lists)): #len(T_lists)でも同じ
        A=j*np.dot(k_v[i], T_lists[j])
        FT = np.exp(A)
        H_sum += H_lists[j] * FT
    w,v = LA.eigh(H_sum)
    print("count",j)

    #ene.append(w)