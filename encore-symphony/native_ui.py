from assets import *
import shutil, subprocess
HASHES={'Encore':'04d1deb0eef007411d87d2d31f6652286f78b174ab190815d9bee58645a2ec49','Symphony':'adcc785a849606ffad8748645348392cbc28a44abc5f40f8180f30f81af89396'}
COMMON=[
 (0x810f0,'次へ','다음'),(0x81550,'確認','확인'),
 (0x81558,'タイトル画面に戻ります。\nよろしいですか？','타이틀 화면으로 돌아갈까요?'),
 (0x81584,'セーブデータを上書きします。\nよろしいですか？','이 저장 데이터를 덮어쓸까요?'),
 (0x815b4,'セーブデータをロードします。\nよろしいですか？','이 저장 데이터를 불러올까요?'),
 (0x8161c,'クイックロードしますか？','빠른 불러오기를 할까요?'),
 (0x818d0,'このゲームは32Bitカラーモードで最適化されています。\nカラーモードを変更していただくとより一層お楽しみになれます。','이 게임은 32비트 색상 모드에 최적화되어 있습니다.\n더 나은 화면으로 즐기려면 색상 모드를 변경해 주세요.'),
 (0x81944,'お知らせ','알림'),(0x81a2c,'コンパイルエラー','컴파일 오류'),
 (0x81a40,'スクリプトネストオーバーフロー','스크립트 중첩 한도 초과'),(0x81a60,'スクリプトネストアンダーフロー','스크립트 중첩 부족'),
 (0x81a80,'レイヤー指定違反','레이어 지정 오류'),(0x81aa0,'テキストフォーマットエラー','텍스트 형식 오류'),
 (0x821d0,'終了確認','종료 확인'),(0x821dc,'本当にゲームを終了しますか？','게임을 종료할까요?')]
def main():
    report={}
    for g,jp,ko in [('Encore','アンコール','앙코르'),('Symphony','シンフォニー','심포니')]:
        org=next(source(g).glob('*.exe'));dst=live(g)/org.name;data=org.read_bytes();assert sha(data)==HASHES[g]
        out=bytearray(data);records=[]
        for off,j,k in COMMON+[(0x816a6,'フェアリーテイル・'+jp,'페어리테일 '+ko)]:
            before,after=j.encode('cp932'),k.encode('cp949')
            if out[off:off+len(before)+1]!=before+b'\0':raise ValueError((g,off,j))
            padding=0
            while off+len(before)+1+padding<len(data) and data[off+len(before)+1+padding]==0 and padding<3:padding+=1
            if len(after)>len(before)+padding:raise ValueError((j,k,len(before),len(after)))
            length=max(len(after),len(before));out[off:off+length+1]=after.ljust(length+1,b'\0')
            records.append({'offset':off,'ja':j,'ko':k})
        digest=sha(out);prev=sha(dst.read_bytes())
        if prev!=digest:
            assert prev==HASHES[g]
            tmp=dst.with_suffix('.ui-pending');tmp.write_bytes(out);assert sha(tmp.read_bytes())==digest;os.replace(tmp,dst)
        assert sha(dst.read_bytes())==digest
        report[g]={'sha256':digest,'original_sha256':HASHES[g],'translator_model':'Codex internal','display_strings':records}
    save('audit/native_ui.json',report);print({g:len(v['display_strings']) for g,v in report.items()})
if __name__=='__main__':main()
