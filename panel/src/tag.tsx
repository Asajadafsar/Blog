import * as React from 'react';
import {
    List,
    Datagrid,
    TextField,
    ReferenceField,
    ListProps,
    Edit,
    SimpleForm,
    TextInput,
    ReferenceInput,
    SelectInput,
    useAuthenticated,
} from 'react-admin';
// Remove the duplicate import statement for List
// import { List, Datagrid, TextField } from 'react-admin';

const TagList = (props) => (
    <List {...props}>
        <Datagrid rowClick="edit">
            <TextField source="id" label="ID" />
            <TextField source="name" label="Tag Name" />
            <TextField source="post_title" label="Post" />
            <TextField source="added_by" label="Added By" />
            <TextField source="status" label="Status" />
        </Datagrid>
    </List>
);



const TagEdit: React.FC = (props) => {
    useAuthenticated(); // Ensure user is authenticated before rendering

    return (
        <Edit {...props}>
            <SimpleForm>
                <TextInput disabled source="id" label="ID" />
                <TextInput source="name" label="Tag Name" />
               
                <SelectInput source="status" label="Status" choices={[
                    { id: 'active', name: 'active' },
                    { id: 'draft', name: 'draft' },
                ]} />
            </SimpleForm>
        </Edit>
    );
};

export { TagList, TagEdit };
