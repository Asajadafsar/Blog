import * as React from 'react';
import { Create, SimpleForm, TextInput, required } from 'react-admin';

const CategoryCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="name" validate={required()} label="Category Name"/>
        </SimpleForm>
    </Create>
);

export default CategoryCreate;
