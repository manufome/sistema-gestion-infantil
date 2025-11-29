import sys

# Read the file
with open('usuarios/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace crear_usuario function (around line 173-189)
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Replace in crear_usuario
    if i == 176 and 'user = form.save()' in line:
        # Replace this line and add new logic
        new_lines.append('            user = form.save(commit=False)\n')
        new_lines.append('            # Set default password: FirstName1234 (e.g., Manuel1234)\n')
        new_lines.append('            default_password = f"{user.first_name.capitalize()}1234"\n')
        new_lines.append('            user.set_password(default_password)\n')
        new_lines.append('            user.needs_password_change = True\n')
        new_lines.append('            user.save()\n')
        new_lines.append('            form.save_m2m()  # Save many-to-many relationships (groups)\n')
        new_lines.append('            \n')
        i += 1
        continue
    
    # Update success message in crear_usuario
    if i == 184 and 'messages.success(request, f' in line and 'creado exitosamente' in line:
        new_lines.append('            messages.success(request, f\'Usuario {user.username} creado exitosamente con rol {user.get_roles()[0].name}. Contraseña inicial: {default_password}\')\n')
        i += 1
        continue
    
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
    
    # Update change_password function
    if i == 273 and 'user = form.save()' in line and i > 270:
        new_lines.append(line)
        i += 1
        new_lines.append('            # Mark that user has changed their password\n')
        new_lines.append('            user.needs_password_change = False\n')
        new_lines.append('            user.save()\n')
        continue
    
    new_lines.append(line)
    i += 1

# Write back
with open('usuarios/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('File updated successfully!')
