FilenameUniqueId=$("mail__" + date + "__%Y%m%d_%H%M%S__%N")
OutputFile="/var/tmp/mail/"$FilenameUniqueId
echo "" > $OutputFile
while read x
do
#echo $x
echo $x >> $OutputFile
done
