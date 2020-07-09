function s = name_from_cell(reg_ex,C)
  s="";
  for i=1:size(C,1)
    if regexp(C{i,1},reg_ex)
      s=C{i,1};
      return
    endif    
  endfor
  
endfunction