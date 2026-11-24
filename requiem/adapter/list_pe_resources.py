import pefile,sys,pathlib
for f in map(pathlib.Path,sys.argv[1:]):
 print('\n===',f,'===')
 pe=pefile.PE(str(f),fast_load=False)
 print('sections',[(s.Name.rstrip(b'\0').decode(errors='replace'),s.SizeOfRawData,s.Misc_VirtualSize) for s in pe.sections])
 if not hasattr(pe,'DIRECTORY_ENTRY_RESOURCE'):
  print('NO RESOURCE'); continue
 for type_entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
  typ=str(type_entry.name) if type_entry.name else str(type_entry.struct.Id)
  for name_entry in type_entry.directory.entries:
   name=str(name_entry.name) if name_entry.name else str(name_entry.struct.Id)
   for lang_entry in name_entry.directory.entries:
    d=lang_entry.data.struct
    print(typ,name,lang_entry.struct.Id,'size',d.Size,'rva',hex(d.OffsetToData))
