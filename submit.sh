for P in $(seq -f "%03g" 1 186)
do
	touch submission/FA$P.nbt
    touch submission/FD$P.nbt
done

for P in $(seq -f "%03g" 1 115)
do
	touch submission/FR$P.nbt
done

cd submission
zip ../submission-`date +%s`.zip ./F*.nbt
cd ..
cp submission-`date +%s`.zip submission.zip

SHA=`openssl sha -sha256 submission.zip | cut -d ' ' -f 2`
URL=https://www.dropbox.com/s/8de8xdxq2fbv6g1/submission-1532349788.zip?dl=0

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
