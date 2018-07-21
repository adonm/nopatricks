for P in {2..186}
do
	touch submission/LA$P.nbt
done

cd submission
zip ../submission.zip ./LA*.nbt
cd ..

SHA=`openssl sha -sha256 submission.zip | cut -d ' ' -f 2`
URL=https://www.dropbox.com/s/zii6lvk3qckp81g/submission.zip?dl=0

curl -L \
  --data-urlencode action=submit \
  --data-urlencode privateID=0f3728f5d9f04de19c2fdf3adb5c4638 \
  --data-urlencode submissionURL=$URL \
  --data-urlencode submissionSHA=$SHA \
  https://script.google.com/macros/s/AKfycbzQ7Etsj7NXCN5thGthCvApancl5vni5SFsb1UoKgZQwTzXlrH7/exec

rm -rf test
mkdir test
cd test
curl -L -s -S -f -o submission.zip $URL
echo $SHA
echo `openssl sha -sha256 submission.zip | cut -d ' ' -f 2`
unzip submission.zip
cd ..
rm -rf test
