import textwrap
from PIL import Image, ImageOps, ImageFont, ImageDraw
from IPython.display import Image as showImage

def mkfig(text,author,date,source):
    foreground = (255, 255, 255)
    text = summary2
    font_path = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf"
    font = ImageFont.truetype(font_path, 20, encoding='unic')
    sourcefont = ImageFont.truetype(font_path, 24, encoding='unic')

    (width, height) = font.getsize(text)

    w_margin = 50
    h_margin = 50
    img_size = (1000, 600)

    bg = Image.new('RGBA', img_size, "#000000")
    draw = ImageDraw.Draw(bg)

    w, h = bg.size

    wraplines = textwrap.wrap("“"+text+"”", width=72)
    y_text = h_margin
    _, height = font.getsize(text)

    for line in wraplines:
        draw.text((w_margin, y_text), line, font=font, fill=foreground)
        y_text += height+5

    x_sourcepos, y_sourcepos = w/6, 6*h/7
    sourcefield = "―"+author+", "+source+", "+date
    draw.text((x_sourcepos, y_sourcepos), sourcefield, font=sourcefont, fill=foreground)

    filename = 'img/'+author+date+source.replace(' ','')+'.png'
    bg.save(filename)
    return filename
