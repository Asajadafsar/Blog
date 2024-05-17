import * as React from 'react';
import { Create, ImageField, ImageInput, SimpleForm, TextInput, required } from 'react-admin';

export const UserCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="username" validate={required()} label="Username"/>
            <TextInput source="password" validate={required()} label="Password"/>
            <TextInput source="phone_number" label="Phone Number" validate={required()} />
            <TextInput source="email" label="Email" validate={required()} />
            <TextInput source="role" label="Role" validate={required()} />
            <ImageInput source="image" label="Product Image" accept="image/*">
                <ImageField source="src" title="title" />
            </ImageInput>
        </SimpleForm>
    </Create>
);
 
export default UserCreate;
