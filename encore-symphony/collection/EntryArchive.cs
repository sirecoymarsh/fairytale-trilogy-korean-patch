using System;
using System.IO;
using System.Text;

namespace FairyCollection {
    internal static class EntryArchive {
        const int Header = 12;
        const int Row = 40;

        static int ReadInt(byte[] input, int position) {
            return BitConverter.ToInt32(input, position);
        }

        static void WriteInt(byte[] output, int position, int value) {
            Buffer.BlockCopy(BitConverter.GetBytes(value), 0, output, position, 4);
        }

        // Only replace 0000.gsc. Preserve later translations, saves' scene offsets and all other members.
        internal static byte[] ReplaceBootstrap(byte[] original, byte[] script) {
            if (original.Length < Header || ReadInt(original, 0) != 0x1424c)
                throw new InvalidDataException("게임 시나리오 파일의 형식을 확인할 수 없어요.");
            int table = ReadInt(original, 4), count = ReadInt(original, 8);
            if (count < 1 || table != (long)count * Row || Header + (long)table > original.Length)
                throw new InvalidDataException("시나리오 파일 목록이 손상되었어요.");
            int data = Header + table, boot = -1;
            for (int i = 0; i < count; i++) {
                int row = Header + i * Row, offset = ReadInt(original, row + 32), size = ReadInt(original, row + 36);
                if (offset < 0 || size < 0 || data + (long)offset + size > original.Length)
                    throw new InvalidDataException("시나리오 파일의 범위가 맞지 않아요.");
                if (Encoding.ASCII.GetString(original, row, 9) == "0000.gsc\0") {
                    if (boot != -1) throw new InvalidDataException("시작 스크립트가 중복되어 있어요.");
                    boot = row;
                }
            }
            if (boot < 0) throw new InvalidDataException("게임의 시작 스크립트를 찾을 수 없어요.");
            int start = ReadInt(original, boot + 32), oldSize = ReadInt(original, boot + 36);
            if (oldSize == script.Length) {
                int i = 0;
                while (i < oldSize && original[data + start + i] == script[i]) i++;
                if (i == oldSize) return original;
            }
            int delta = script.Length - oldSize;
            byte[] result = new byte[checked(original.Length + delta)];
            Buffer.BlockCopy(original, 0, result, 0, data + start);
            Buffer.BlockCopy(script, 0, result, data + start, script.Length);
            int end = data + start + oldSize;
            Buffer.BlockCopy(original, end, result, end + delta, original.Length - end);
            for (int i = 0; i < count; i++) {
                int row = Header + i * Row;
                if (row == boot) { WriteInt(result, row + 36, script.Length); continue; }
                int offset = ReadInt(original, row + 32), size = ReadInt(original, row + 36);
                if (offset >= start + oldSize) WriteInt(result, row + 32, offset + delta);
                else if (offset + (long)size > start)
                    throw new InvalidDataException("게임 스크립트의 파일 범위가 겹칩니다.");
            }
            return result;
        }

        internal static void Select(string target, string source) {
            byte[] script = File.ReadAllBytes(source);
            string temp = target + "." + Guid.NewGuid().ToString("N") + ".hub-new";
            try {
                for (int attempt = 0; attempt < 3; attempt++) {
                    var before = File.GetLastWriteTimeUtc(target);
                    byte[] current = File.ReadAllBytes(target);
                    byte[] result = ReplaceBootstrap(current, script);
                    if (Object.ReferenceEquals(current, result)) return;
                    File.WriteAllBytes(temp, result);
                    if (File.GetLastWriteTimeUtc(target) != before) continue;
                    File.Replace(temp, target, null);
                    return;
                }
                throw new IOException("게임 파일이 갱신 중이에요. 잠시 후 다시 열어 주세요.");
            } finally {
                if (File.Exists(temp)) File.Delete(temp);
            }
        }
    }
}
