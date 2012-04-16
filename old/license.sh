for cc in `find src   -name "*.py"`; do
	cat license_text.txt > /tmp/out
	cat $cc >> /tmp/out 
	mv /tmp/out $cc
	echo $cc
done
