package org.MGA;

import com.intellij.openapi.actionSystem.*;
import com.intellij.openapi.command.WriteCommandAction;
import com.intellij.openapi.editor.*;
import com.intellij.openapi.project.Project;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.InterruptedException;

/**
 * @author Qs
 */
public class GeneAnno extends AnAction {

    @Override
    public void actionPerformed(AnActionEvent event) {
        //Get all the required data from data keys
        final Project project = event.getData(PlatformDataKeys.PROJECT);
        final Editor editor = event.getData(PlatformDataKeys.EDITOR);

        //Document represents the file text selected by user
        final Document document = editor.getDocument();
        final SelectionModel selectionModel = editor.getSelectionModel();

        //Get the start and end position of the selection
        final int start = selectionModel.getSelectionStart();
        //final int end = selectionModel.getSelectionEnd();

        //Get the text selected by user
        String selectedText = selectionModel.getSelectedText();

        //Get the max offset of the generated annotation
        int maxOffset = document.getTextLength() - 1;

        //Get the line number of selected text
        int curLineNumber = document.getLineNumber(start);
        int preLineStartOffset = start - document.getLineStartOffset(curLineNumber);

        //Get the insert position of generated annotation
       // int insertOffset = maxOffset > preLineStartOffset ? preLineStartOffset : maxOffset;
        int insertOffset =  start ;

        //The operation of doc must be thrown in Runnable api and handled within a new thread in IDEA
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                document.insertString(insertOffset, geneAnno(selectedText, preLineStartOffset));
            }
        };

        WriteCommandAction.runWriteCommandAction(project, runnable);
    }

    /**
     * Make action visible and available only when existing project and editor and some text in the editor
     *     is selected.
     * @param event
     */
    @Override
    public void update(AnActionEvent event) {
        //Get required data keys
        //final Project project = event.getProject();
        final Editor editor = event.getData(PlatformDataKeys.EDITOR);
        final SelectionModel selectionModel = editor.getSelectionModel();

        //Set visibility only in case of existing project and editor and if some text in the editor is selected
        event.getPresentation().setVisible(editor != null && selectionModel.hasSelection());
    }

    /**
     * Get the annotation of method codes by calling python script.
     * @param code
     * @return
     */
    public String geneAnno(String code, int offset) {
        //annotation contains the returned annotation of code
        String annotation = "fuck\n";

        try {
            String[] args = new String[] {"python", "lib\\geneAnno.py", code};
            Process process = Runtime.getRuntime().exec(args);
            //Get the output of python file with 'print' method
            BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
            annotation = in.readLine();
            in.close();
            process.waitFor();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        for (int i = 0;i < offset;i ++ ) {
            annotation = annotation + ' ';
        }

        return annotation;
    }
}