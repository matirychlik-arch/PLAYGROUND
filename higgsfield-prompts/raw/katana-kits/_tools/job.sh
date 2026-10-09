set -u
cd /home/user/kat
mkdir -p kits ref an log
dl(){ # slug url sha
  d=kits/$1; mkdir -p $d; f=$d/$(basename $2)
  [ -s $f ] || curl -sSfL --retry 3 -o $f "$2" || { echo "DL FAIL $1 $2"; return; }
  echo "$3  $f" | sha256sum -c --quiet - && echo "SHA OK $1 $(basename $2) $(stat -c%s $f)" || echo "SHA BAD $1 $(basename $2)"
  case $f in *.zip) unzip -qo $f -d $d/x 2>/dev/null;; *.gz) mkdir -p $d/x && tar xzf $f -C $d/x 2>/dev/null || { mv $f $f.raw; gunzip -c $f.raw > $d/x/$(basename $f .gz) 2>/dev/null; };; esac
}
dl lights-out https://d2ol7oe51mr4n9.cloudfront.net/user_3DiGlp7Voza2aJTOndWCQ2iEJ9Z/4896a7b9-475a-4bc2-a79d-250bacc451b1.gz 50701fdf4d2e873e0be784839efc8c0de5908b1daee6fca3a77abe7c1066d887
dl travel-edit https://d2ol7oe51mr4n9.cloudfront.net/user_3DiGlp7Voza2aJTOndWCQ2iEJ9Z/e189cbe2-5ba4-4b49-94e7-68c8aad7f99c.gz 34e427f94864834cb9d0d56663e44a1aa3e20a02faceb737198d1a2f91c13b6a
dl living-lab https://d2ol7oe51mr4n9.cloudfront.net/user_3GDl8vBjBYMIQhCvMHnwvt4vSfX/76b25ce2-2bb7-4a2f-817b-9576f4c96a84.zip 79633c3d5e51e0d2d1dd28eace020265d3635ad4e4798565be44fc6d0119ddb4
dl many-lies https://d2ol7oe51mr4n9.cloudfront.net/user_34sAKim8cOqbidZN9XoRhYrfbCs/2a9fd976-287f-42ae-83e2-b8b1166e069e.gz 1ddde5d4144fd160e27cd307c83a54566c193103fbb24260daa518e7599cb268
dl physical-body https://d2ol7oe51mr4n9.cloudfront.net/user_34sAKim8cOqbidZN9XoRhYrfbCs/dc4a13fc-832c-44d4-aa4f-0293a4f3b99d.gz af0ac9f3fd2a21a895ee2ca513903dd368efe72c91a6d6445d2ca50abf5dfe31
dl physical-body https://d2ol7oe51mr4n9.cloudfront.net/user_34sAKim8cOqbidZN9XoRhYrfbCs/b6bcbeda-5fd1-4056-a1c6-febef66cedb6.gz 6e93c61d81d8ee4f73ad6e4384ebff83d2a47b2d1f9f0a624e209ea9f2c9a481
dl let-me-show-you https://d2ol7oe51mr4n9.cloudfront.net/user_3BtsEcww7blE0e9EKFuXmUaobas/c154e921-66d0-47bc-8346-90b41e8619bc.zip 17b91d438febbc86a28dde1027e70be02c57b0ab7aaa728e6c26297f88180c04
dl the-boys https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/a92da659-07fd-4ec8-a0c5-764e97af778a.zip b7818851b9f1799051185a12f26b33f4cae2b60241d842099eab85581f7e0b1e
for p in 5f13a21d-089b-43f2-9324-4c5da639bdc5:0e45d496aba2ba13ef8235a904ee8976fb0515dd968fbe2b1668876fc032d6e5 a0f00dea-be98-4f56-837b-5e6edd74bd91:e2042f3c93f468124b637df30c2f9a71da6f794e3c71fc83cbe873c6cca83dab 534f6bbe-a560-4fb3-822f-d0380bcb0212:319d1e55711908df5a651896152d6362af1d73ca65c8a258bed8511f2ce698e3 0a6069ec-85d2-4898-95b1-186a1691ca36:25ebba58462b9f7554a80062acf79ad39bb9b42f7e867308d03e3cb43ac73f5a 466eb4be-1087-4ef3-b3cf-5fa32c1abe59:365844b74a147bdcf80cc420b5dfe50d9b6fb86939aa4006d9ef30a1c8371b4f 04cf4d52-ab79-4ae3-b2d1-5aee84ad21ae:91cccd2e324003b908e03912af32733b03d932332f7b0c9469d4ff0ea877174e f29381ed-13ff-4091-ac91-9a73c5e6a744:25a75ec52dc602543ca28ca9bdb2153aa12fc520beec06c9a893909446924436 5a9ae5ca-a19a-41ce-a216-dffc90d6be48:501eea65071a82ce81c994ff0fd7d772f794ea159e107e29b1b49ea8c803e113 24d0d3a0-a05c-4ed9-b8f4-18de6c48e51d:09f132802b8588bda3493c6f4837ca1b48b1386b247752b498ff90bf5cef1c25 00006228-b593-4057-a34c-613c422c5d84:246b84fdac24fb2c82f3c0673daee04b297d34068ad1053e91ba426158a49dbe 9f37b64e-b906-4d89-baf1-571bb03650ad:cf266028b4f98adf9288ced18e5cb0c41c1214758ad650118dd8224c742001f7; do dl pink-collage https://d2ol7oe51mr4n9.cloudfront.net/user_34sAKim8cOqbidZN9XoRhYrfbCs/${p%%:*}.gz ${p##*:}; done
echo "== KITS DONE"; find kits -path '*/x/*' -type f -printf '%s %p\n' | sort -k2 > log/kits_listing.txt; wc -l log/kits_listing.txt
B=https://static-public-media.higgsfield.ai/katana-presets
for s in blue-eyes:53cf8640-34b7-437c-8075-2ec9e914783a.mp4 car-edit:ab4d2a58-1e39-4b7c-807d-e7edf036adc1.mp4 chrome-orbit:c50e793c-2d2d-41e2-a24f-1f6f9ae11de9.mp4 dark-and-moody:3d808c8a-799b-4de7-a936-9ce6ebc499d3.mp4 dark-aura:ca11c5a5-0a59-4d64-a363-a3c228a905d8.mp4 dreamy-streetwear:641fc2de-b72a-4e3d-8dde-aa1ae8e94578.mp4 frame-dance:published/2d62b7adae19369b1bb267b2a1e1a1b15857eaa3e6090c67b8aeea2bab5b0dda grunge-aura:published/fbbde304b66c4326ebff9b68efae79179a54ceba0284e8de5092a288bf190c7c kawaii-pop:published/37a305221afe1e5d4e7c0b849282e5f93c4fa6afa24136a33d530daeb26482ef last-katana:published/6b020a6cd3ce94d3bae168f71ce5b2f98c641d714104957a60991889b3a0d659 many-lies:published/05b6839dc7315eb2bc06bbc9731abb5345cca465ef37bb642ea1262aa559967d nocturne:d5efd859-2c60-4e06-9197-8bb66e6e9af1.mp4 outfit-check:a7c2bc28-b911-42a8-a9ac-0c6151a21324.mp4 painting-flow:c27b67f5-092a-40d3-990c-23ece2cde617.mp4 power-suit:131af3b6-350e-4bee-8763-c56591d51468.mp4 star:d6596e20-cb5b-4a0b-9305-03553168b20e.mp4 tiger-eyes:11431a22-d477-4899-ad77-fdb3b3516983.mp4 tokyo-bloom:published/1eb68ea299fd6f45f660066f0e6b51840bc8da17368f9075920229b850f2c9ab xerox-2:553c4b6f-1535-40f3-9678-ad93be50ff12.mp4 xerox-3:f9c9b4b6-c70e-41f5-877b-4ca08e380190.mp4; do
  n=${s%%:*}; u=$B/${s#*:}; mkdir -p an/$n/ref
  [ -s an/$n/ref/ref.mp4 ] || curl -sSfL --retry 3 -o an/$n/ref/ref.mp4 "$u" || { echo "REF FAIL $n"; continue; }
  echo "REF $n $(ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,nb_frames -of csv=p=0 an/$n/ref/ref.mp4 | tr '\n' ' ')"
  python3 $HF_WORKFLOWS/katana/scripts/analyze_ref.py --review-size --quiet an/$n > log/an_$n.log 2>&1 && echo "AN OK $n" || echo "AN FAIL $n"
done
echo "== ALL DONE"
