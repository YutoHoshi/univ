
# スクリプトの実行ディレクトリを取得
current_dir=$(pwd)


python3 vasp.py -pot

#scf計算
python3 vasp.py -scf
vasp_std
mkdir scf
cp * scf
sed -i 's/isif=.*/isif=0/' vasp.py #isif=0に置換

#構造緩和(opt)準備
if [ "$1" == "first" ]; then
	mkdir opt
	cp * opt
	cd opt
	cp CONTCAR POSCAR
	cd ..
fi

#band計算
python3 vasp.py -band
vasp_std
mkdir bands
cp * bands
python3 plotbandef.py
cp scf/KPOINTS KPOINTS
cp scf/*CAR .
cp scf/CHG CHG

#wannier準備
python3 vasp.py -wannier
vasp_std
cp wannier90.win wannier90.win_VASPmade

#wannier90
wannier90.x wannier90

# カレントディレクトリを元に戻す
cd "$current_dir"

# スクリプトの終了
echo "自動化が完了しました。"

