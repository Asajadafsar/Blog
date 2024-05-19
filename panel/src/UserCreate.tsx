import * as React from 'react';
import { Create, ImageField, ImageInput, SimpleForm, TextInput, SelectInput, required } from 'react-admin';

export const UserCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="username" validate={required()} label="Username" />
            <TextInput source="password" validate={required()} label="Password" />
            <TextInput source="phone_number" label="Phone Number" validate={required()} />
            <TextInput source="email" label="Email" validate={required()} />
            <SelectInput 
                source="role" 
                label="Role" 
                choices={[
                    { id: 'admin', name: 'admin' },
                    { id: 'user', name: 'user' },
                ]}
                validate={required()}
            />
            <ImageInput source="profile_picture" label="Profile Picture" accept="image/*">
                <ImageField source="src" title="title" />
            </ImageInput>
        </SimpleForm>
    </Create>
);

export default UserCreate;
