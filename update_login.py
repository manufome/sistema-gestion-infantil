import sys

# Read the file
with open('usuarios/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace UserLoginView get_success_url
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Update UserLoginView get_success_url
    if i == 66 and 'def get_success_url(self):' in line:
        new_lines.append(line)
        i += 1
        new_lines.append('        user = self.request.user\n')
        new_lines.append('        messages.success(self.request, f\'Bienvenido {user.username} a la plataforma de la fundación\')\n')
        new_lines.append('        \n')
        new_lines.append('        # Check if user needs to change password\n')
        new_lines.append('        if user.needs_password_change:\n')
        new_lines.append('            messages.warning(self.request, \'⚠️ Por favor actualiza tu contraseña inicial. Ve a Configuración para cambiarla.\')\n')
        new_lines.append('        \n')
        # Skip next 2 lines (old implementation)
        i += 2
        continue
    
    new_lines.append(line)
    i += 1

# Write back
with open('usuarios/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Login view updated successfully!')
