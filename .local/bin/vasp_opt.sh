#並列数。一人でサーバーを占有するにしても20にする。
nmp=12

# スクリプトの実行ディレクトリを取得
#current_dir=$(pwd)

#novitiateにログインし、サーバー上のコアを使う場合は以下をコメントインする
vasphome=/usr/vasp/bin
wannierhome=/usr/wannier90/bin
vasp=${vasphome}/vasp_std
wannier90=${wannierhome}/wannier90.x

#oneapiを導入した場合は、以下をコメントインする（ubuntu、novitiate共通）
source /opt/intel/oneapi/setvars.sh > /dev/null
export OMP_PLACES=cores
export OMP_PROC_BIND=close
export OMP_STACKSIZE=512m
export MPI_GROUP_MAX=20000
export MPI_COMM_MAX=1000

#scf計算
cp CONTCAR POSCAR
python3 vasp.py -scf
mpirun -np $nmp $vasp
mkdir scf
cp * scf

#band計算
python3 vasp.py -band
mpirun -np $nmp $vasp
mkdir bands
cp * bands

#wannier準備
python3 plotbandef.py
cp scf/KPOINTS KPOINTS
cp scf/*CAR .
cp scf/CHG CHG
python3 vasp.py -wannier
mpirun -np $nmp $vasp
cp wannier90.win wannier90.win_VASPmade

#wannier90
wannier90.x wannier90

# カレントディレクトリを元に戻す
cd "$current_dir"

# スクリプトの終了
echo "自動化が完了しました。"
