for P in {100..186}
do
	touch submission/LA$P.nbt
done

cd submission
zip ../submission.zip *
cd ..

SHA=`openssl sha -sha256 submission.zip | cut -d ' ' -f 2`
URL=`curl --upload-file ./submission.zip https://transfer.sh/submission.zip`

curl -L \
  --data-urlencode action=submit \
  --data-urlencode privateID=0f3728f5d9f04de19c2fdf3adb5c4638 \
  --data-urlencode submissionURL=$URL \
  --data-urlencode submissionSHA=$SHA \
  https://script.google.com/macros/s/AKfycbzQ7Etsj7NXCN5thGthCvApancl5vni5SFsb1UoKgZQwTzXlrH7/exec

