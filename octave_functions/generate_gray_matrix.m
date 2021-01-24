function m_res = generate_gray_matrix(steps)
  % genera una matriz de grises en orden creciente, del negro al blanco.
  % steps marca la resolución de la escala
  
  m_res = ones(steps,3);
  for i = 1:steps
    m_res(i,:) = m_res(i,:)*i/steps;
  endfor
 endfunction